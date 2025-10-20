import json
import yaml
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from git import Repo, InvalidGitRepositoryError
from .discover import build_manifest
from .analyze_static import run_flake8, run_bandit, run_semgrep
from .score import score_findings, score_findings_from_config
from .consolidate import to_phases, to_phases_from_config, generate_enhanced_recommendation
from .ai_apply import propose_patches
from .diffscan import changed_files
from .utils import write_json, write_text
from .prompt_generation import generate_patch_prompt

console = Console()


def _validate_repository(repo_root: Path) -> None:
    """Validate that the repository path exists and is a git repository."""
    if not repo_root.exists():
        console.print(f"[red]Error:[/red] Repository path does not exist: {repo_root}")
        raise FileNotFoundError(f"Repository not found: {repo_root}")

    if not repo_root.is_dir():
        console.print(f"[red]Error:[/red] Path is not a directory: {repo_root}")
        raise NotADirectoryError(f"Not a directory: {repo_root}")

    try:
        Repo(repo_root)
    except InvalidGitRepositoryError:
        console.print(f"[yellow]Warning:[/yellow] {repo_root} is not a git repository")
        console.print("Git-based features (delta review, churn analysis) will be unavailable")


def _load_engine_config(repo_root: Path):
    """Load engine configuration with error handling."""
    config_path = Path(repo_root, "config", "engine.yaml")

    if not config_path.exists():
        console.print(f"[red]Error:[/red] Configuration file not found: {config_path}")
        console.print("Expected: config/engine.yaml in repository root")
        raise FileNotFoundError(f"Config not found: {config_path}")

    try:
        cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        return cfg
    except yaml.YAMLError as e:
        console.print(f"[red]Error:[/red] Invalid YAML in {config_path}")
        console.print(f"Details: {e}")
        raise

def run_full_pass(repo: str, outputs: str, ai_override: Optional[str] = None):
    """Run full code review pass with progress tracking and error handling."""
    repo_root = Path(repo).resolve()
    out_dir = Path(outputs).resolve()

    # Validate repository
    _validate_repository(repo_root)

    # Load configuration
    try:
        cfg = _load_engine_config(repo_root)
    except (FileNotFoundError, yaml.YAMLError):
        console.print("[red]Failed to load configuration. Aborting.[/red]")
        return

    # Create output directory
    out_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]Output directory:[/green] {out_dir}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:

        # 1) Manifest
        task = progress.add_task("Building manifest...", total=100)
        try:
            manifest = build_manifest(repo_root, Path(repo_root, cfg["include_exclude"]))
            write_json(out_dir / "000_manifest.json", manifest.dict())
            progress.update(task, completed=100)
            console.log(f"[green]✓[/green] Wrote 000_manifest.json ({len(manifest.files)} files)")
        except Exception as e:
            progress.update(task, completed=100)
            console.print(f"[red]Error building manifest:[/red] {e}")
            return

        # 2) Static analysis
        task = progress.add_task("Running static analysis...", total=3)
        findings = []
        try:
            findings += run_flake8(repo_root, Path(repo_root, cfg["tools"]["flake8_config"]))
            progress.update(task, advance=1, description="Running flake8... ✓")
            findings += run_bandit(repo_root, Path(repo_root, cfg["tools"]["bandit_config"]))
            progress.update(task, advance=1, description="Running bandit... ✓")
            findings += run_semgrep(repo_root, Path(repo_root, cfg["tools"]["semgrep_rules"]))
            progress.update(task, advance=1, description="Running semgrep... ✓")

            write_json(out_dir / "010_static_findings.json", [f.dict() for f in findings])
            console.log(f"[green]✓[/green] Wrote 010_static_findings.json ({len(findings)} findings)")
        except Exception as e:
            progress.update(task, completed=3)
            console.print(f"[yellow]Warning:[/yellow] Static analysis partially failed: {e}")
            console.print("Continuing with available findings...")

        # 3) Scoring
        task = progress.add_task("Scoring findings...", total=100)
        try:
            if "scoring" in cfg:
                scored = score_findings_from_config(findings, cfg["scoring"])
            else:
                scored = score_findings(findings)
            write_json(out_dir / "030_scores.json", [s.dict() for s in scored])
            progress.update(task, completed=100)
            console.log(f"[green]✓[/green] Wrote 030_scores.json ({len(scored)} scored items)")
        except Exception as e:
            progress.update(task, completed=100)
            console.print(f"[red]Error scoring findings:[/red] {e}")
            return

        # 4) Human recommendations (enhanced format with rationale)
        task = progress.add_task("Generating recommendations...", total=100)
        try:
            scored_sorted = sorted(scored, key=lambda s: s.value_importance * (6 - s.difficulty_risk), reverse=True)

            recs = ["# Code Quality Recommendations\n\n"]
            recs.append(f"**Total Issues**: {len(scored_sorted)} | **Estimated Total Effort**: {sum(s.est_hours for s in scored_sorted):.1f}h\n\n")
            recs.append("---\n\n")

            # Generate enhanced recommendations for top findings (limit to avoid huge files)
            for s in scored_sorted[:20]:  # Top 20 by priority
                recs.append(generate_enhanced_recommendation(s))

            write_text(out_dir / "040_recommendations.md", "".join(recs))
            progress.update(task, completed=100)
            console.log(f"[green]✓[/green] Wrote 040_recommendations.md (top 20 of {len(scored_sorted)} issues)")
        except Exception as e:
            progress.update(task, completed=100)
            console.print(f"[yellow]Warning:[/yellow] Recommendations generation failed: {e}")

        # 5) Phased plan (use config-driven routing)
        task = progress.add_task("Creating phased plan...", total=100)
        try:
            phases = to_phases_from_config(scored, cfg.get("phasing", []))
            plan_md = ["# Phased Improvement Plan\n"]
            for name, items in phases.items():
                if len(items) == 0:
                    continue  # Skip empty phases
                plan_md.append(f"\n## {name}\n")
                for it in items:
                    plan_md.append(f"- {it.finding.file}:{it.finding.line} — {it.finding.message} "
                                   f"(V={it.value_importance:.1f}, D={it.difficulty_risk:.1f}, ~{it.est_hours}h)")
            write_text(out_dir / "050_phased_plan.md", "\n".join(plan_md))
            progress.update(task, completed=100)
            console.log(f"[green]✓[/green] Wrote 050_phased_plan.md ({len([p for p in phases.values() if p])} phases)")
        except Exception as e:
            progress.update(task, completed=100)
            console.print(f"[yellow]Warning:[/yellow] Phased plan generation failed: {e}")

    # 6) AI apply (optional)
    provider = ai_override or cfg["ai"]["provider"]
    if provider and provider != "none":
        console.print(f"\n[cyan]AI Provider:[/cyan] {provider}")
        prompts = []
        for it in scored[:20]:  # cap to avoid token blowups
            # Use enhanced prompt with file context
            prompt = generate_patch_prompt(
                it.finding,
                context_lines=5,
                include_system_prompt=True
            )
            prompts.append(prompt)
        try:
            with console.status(f"[cyan]Calling {provider} API...") as status:
                patches, cost_info = propose_patches(
                    provider,
                    cfg["ai"]["model"][provider],
                    prompts,
                    max_output_tokens=cfg["ai"]["max_output_tokens"],
                    temperature=cfg["ai"]["temperature"],
                    rate_limit_rps=cfg["ai"]["rate_limit_rps"],
                    return_cost=True
                )
                md = "# AI Patch Suggestions\n\n" + "\n\n---\n\n".join(patches)
                write_text(out_dir / "060_ai_patch_suggestions.md", md)

            # Log cost information
            console.log(f"[green]✓[/green] Wrote 060_ai_patch_suggestions.md ({len(patches)} patches)")
            console.print(f"  [cyan]Total Cost:[/cyan] ${cost_info['total_cost']:.4f}")
            console.print(f"  [cyan]Tokens:[/cyan] {cost_info['total_input_tokens']} input + {cost_info['total_output_tokens']} output = {cost_info['total_tokens']} total")
            console.print(f"  [cyan]Avg Cost/Request:[/cyan] ${cost_info['cost_per_request']:.4f}")
        except Exception as ex:
            console.print(f"[yellow]AI patch step skipped:[/yellow] {ex}")

    # Summary
    console.print("\n" + "="*70)
    console.print(f"[bold green]✓ Code Review Complete![/bold green]")
    console.print("="*70)
    console.print(f"  Repository: {repo_root}")
    console.print(f"  Findings: {len(findings)}")
    console.print(f"  Scored Items: {len(scored)}")
    console.print(f"  Total Effort: {sum(s.est_hours for s in scored):.1f} hours")
    console.print(f"  Output: {out_dir}")
    console.print("="*70 + "\n")

def run_delta_pass(repo: str, outputs: str):
    repo_root = Path(repo).resolve()
    out_dir = Path(outputs).resolve()
    files = changed_files(repo_root)
    summary = {"changed_files": files}
    write_json(out_dir / "070_delta_review.json", summary)
    console.log("Wrote 070_delta_review.json")
