# Future Features & Roadmap

This document outlines planned enhancements for AutoRev AI Code Review.

---

## Phase 1: Enhanced Analysis Features

### 1.1 Project Token & Cost Estimator

**Purpose**: Provide upfront cost estimates before running expensive AI analysis.

**Features**:
- **Pre-scan Analysis**: Count tokens across all filtered files before AI review
- **Cost Calculator**: Estimate cost based on provider and model
- **Budget Controls**: Set maximum token/cost limits per analysis
- **Historical Tracking**: Show average costs per repository over time

**Implementation**:
```python
# src/crengine/cost_estimator.py

from pathlib import Path
from typing import Dict, List
import tiktoken

class CostEstimator:
    """Estimates tokens and costs before AI analysis"""

    # Pricing per 1M tokens (as of 2025)
    PRICING = {
        'gpt-4o-mini': {'input': 0.150, 'output': 0.600},  # $0.15 / $0.60 per 1M tokens
        'gpt-4o': {'input': 2.50, 'output': 10.00},
        'claude-3-5-sonnet': {'input': 3.00, 'output': 15.00},
        'claude-3-haiku': {'input': 0.25, 'output': 1.25},
    }

    def __init__(self, model: str = 'gpt-4o-mini'):
        self.model = model
        self.encoding = tiktoken.get_encoding('cl100k_base')

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.encoding.encode(text))

    def estimate_repository(
        self,
        files: List[Path],
        repo_root: Path
    ) -> Dict:
        """
        Estimate tokens and costs for repository analysis

        Returns:
            {
                'total_files': int,
                'total_characters': int,
                'estimated_input_tokens': int,
                'estimated_output_tokens': int,
                'estimated_cost': float,
                'by_language': {...},
                'largest_files': [...]
            }
        """
        total_chars = 0
        total_tokens = 0
        by_language = {}
        file_sizes = []

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                chars = len(content)
                tokens = self.count_tokens(content)

                total_chars += chars
                total_tokens += tokens

                # Track by language
                ext = file_path.suffix.lower()
                if ext not in by_language:
                    by_language[ext] = {'files': 0, 'tokens': 0, 'chars': 0}
                by_language[ext]['files'] += 1
                by_language[ext]['tokens'] += tokens
                by_language[ext]['chars'] += chars

                # Track largest files
                file_sizes.append({
                    'file': str(file_path.relative_to(repo_root)),
                    'tokens': tokens,
                    'chars': chars
                })
            except (UnicodeDecodeError, IOError):
                continue

        # Sort by token count
        file_sizes.sort(key=lambda x: x['tokens'], reverse=True)

        # Estimate output tokens (response is typically 20-30% of input for code review)
        estimated_output = int(total_tokens * 0.25)

        # Calculate cost
        pricing = self.PRICING.get(self.model, self.PRICING['gpt-4o-mini'])
        input_cost = (total_tokens / 1_000_000) * pricing['input']
        output_cost = (estimated_output / 1_000_000) * pricing['output']
        total_cost = input_cost + output_cost

        return {
            'total_files': len(files),
            'total_characters': total_chars,
            'estimated_input_tokens': total_tokens,
            'estimated_output_tokens': estimated_output,
            'estimated_cost_usd': round(total_cost, 4),
            'cost_breakdown': {
                'input': round(input_cost, 4),
                'output': round(output_cost, 4),
            },
            'by_language': by_language,
            'largest_files': file_sizes[:10],  # Top 10
            'model': self.model,
        }

    def format_estimate(self, estimate: Dict) -> str:
        """Format estimate as human-readable text"""
        lines = [
            f"# Cost Estimate for {estimate['model']}",
            "",
            f"**Total Files**: {estimate['total_files']}",
            f"**Total Characters**: {estimate['total_characters']:,}",
            f"**Estimated Input Tokens**: {estimate['estimated_input_tokens']:,}",
            f"**Estimated Output Tokens**: {estimate['estimated_output_tokens']:,}",
            "",
            f"**Estimated Cost**: ${estimate['estimated_cost_usd']:.4f}",
            f"  - Input: ${estimate['cost_breakdown']['input']:.4f}",
            f"  - Output: ${estimate['cost_breakdown']['output']:.4f}",
            "",
            "## By Language",
            ""
        ]

        for ext, stats in sorted(estimate['by_language'].items(),
                                  key=lambda x: x[1]['tokens'],
                                  reverse=True):
            lines.append(f"- **{ext}**: {stats['files']} files, "
                        f"{stats['tokens']:,} tokens")

        lines.extend([
            "",
            "## Largest Files",
            ""
        ])

        for file_info in estimate['largest_files']:
            lines.append(f"- `{file_info['file']}`: {file_info['tokens']:,} tokens")

        return "\n".join(lines)
```

**API Integration**:
```python
# In src/api/main.py

@app.post("/api/analysis/estimate")
async def estimate_analysis(request: AnalysisRequest):
    """
    Estimate tokens and cost before running analysis

    Returns cost estimate without actually running AI review
    """
    # Clone and filter repository
    repo_path = clone_repository(request.repo_url, request.branch)
    filtered_files = filter_repository_files(repo_path, config_path)

    # Estimate cost
    estimator = CostEstimator(model='gpt-4o-mini')
    estimate = estimator.estimate_repository(filtered_files, repo_path)

    return {
        "estimate": estimate,
        "formatted": estimator.format_estimate(estimate),
        "warning": "This is an estimate. Actual costs may vary by ±20%."
    }
```

**UI Integration**:
```typescript
// Show before starting analysis
const estimate = await fetch('/api/analysis/estimate', {
  method: 'POST',
  body: JSON.stringify({ repository, branch })
});

// Display confirmation dialog
<EstimateDialog>
  <p>This analysis will cost approximately <strong>${estimate.cost}</strong></p>
  <p>Processing {estimate.files} files ({estimate.tokens.toLocaleString()} tokens)</p>
  <button onClick={confirmAnalysis}>Proceed</button>
  <button onClick={cancel}>Cancel</button>
</EstimateDialog>
```

---

### 1.2 Interactive Code Diagram Generator

**Purpose**: Visualize codebase architecture, dependencies, and module relationships.

**Features**:
- **Multi-Tier Architecture Diagrams**: Separate frontend, backend, database, services
- **Module Dependency Graphs**: Show import/export relationships
- **Call Flow Diagrams**: Trace function calls across modules
- **Data Flow Visualization**: Track data through the system
- **Interactive Navigation**: Click modules to zoom in/out
- **Export Options**: PNG, SVG, Mermaid, PlantUML formats

**Architecture**:
```
Codebase Files
      ↓
AST Parser (Tree-sitter)
      ↓
Dependency Extractor
      ↓
Tier Classifier
      ↓
Graph Generator
      ↓
Diagram Renderer
```

**Implementation**:
```python
# src/crengine/diagram_generator.py

from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import networkx as nx
import json

@dataclass
class Module:
    """Represents a code module"""
    name: str
    file_path: str
    tier: str  # 'frontend', 'backend', 'database', 'service', 'utility'
    imports: List[str]
    exports: List[str]
    functions: List[str]
    classes: List[str]
    dependencies: Set[str]  # Other modules this depends on

@dataclass
class Tier:
    """Represents an architectural tier"""
    name: str
    description: str
    modules: List[Module]
    color: str

class DiagramGenerator:
    """Generates interactive architecture diagrams"""

    TIERS = {
        'frontend': Tier(
            name='Frontend',
            description='User interface and presentation layer',
            modules=[],
            color='#61DAFB'  # React blue
        ),
        'backend': Tier(
            name='Backend',
            description='Business logic and API layer',
            modules=[],
            color='#68A063'  # Node green
        ),
        'database': Tier(
            name='Database',
            description='Data persistence layer',
            modules=[],
            color='#336791'  # PostgreSQL blue
        ),
        'service': Tier(
            name='Services',
            description='External integrations and microservices',
            modules=[],
            color='#FF6B6B'  # Service red
        ),
        'utility': Tier(
            name='Utilities',
            description='Shared utilities and helpers',
            modules=[],
            color='#95A5A6'  # Gray
        ),
    }

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.modules: Dict[str, Module] = {}
        self.graph = nx.DiGraph()

    def classify_tier(self, file_path: Path) -> str:
        """Classify file into architectural tier"""
        path_str = str(file_path)

        # Frontend patterns
        if any(p in path_str for p in ['components/', 'pages/', 'app/', 'ui/', 'views/']):
            if file_path.suffix in ['.tsx', '.jsx', '.vue', '.svelte']:
                return 'frontend'

        # Backend patterns
        if any(p in path_str for p in ['api/', 'routes/', 'controllers/', 'services/']):
            if file_path.suffix in ['.py', '.js', '.ts', '.go', '.java']:
                return 'backend'

        # Database patterns
        if any(p in path_str for p in ['models/', 'migrations/', 'schema/', 'db/']):
            return 'database'

        # Service patterns
        if any(p in path_str for p in ['integrations/', 'external/', 'clients/']):
            return 'service'

        # Default to utility
        return 'utility'

    def extract_dependencies(self, file_path: Path) -> Module:
        """Extract module information from file"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, IOError):
            return None

        # Parse imports (simplified - would use Tree-sitter in production)
        imports = []
        exports = []
        functions = []
        classes = []

        for line in content.split('\n'):
            line = line.strip()

            # Python imports
            if line.startswith('import ') or line.startswith('from '):
                module = line.split()[1].split('.')[0]
                imports.append(module)

            # JavaScript/TypeScript imports
            elif line.startswith('import '):
                parts = line.split()
                if 'from' in parts:
                    idx = parts.index('from')
                    module = parts[idx + 1].strip("'\"")
                    imports.append(module)

            # Function definitions
            elif line.startswith('def ') or line.startswith('function '):
                func_name = line.split('(')[0].split()[-1]
                functions.append(func_name)

            # Class definitions
            elif line.startswith('class '):
                class_name = line.split('(')[0].split()[1].strip(':')
                classes.append(class_name)

        tier = self.classify_tier(file_path)

        return Module(
            name=file_path.stem,
            file_path=str(file_path.relative_to(self.repo_root)),
            tier=tier,
            imports=imports,
            exports=exports,
            functions=functions,
            classes=classes,
            dependencies=set(imports)
        )

    def analyze_repository(self, files: List[Path]) -> Dict:
        """Analyze repository and build dependency graph"""
        # Extract modules
        for file_path in files:
            module = self.extract_dependencies(file_path)
            if module:
                self.modules[module.name] = module
                self.TIERS[module.tier].modules.append(module)
                self.graph.add_node(module.name, **module.__dict__)

        # Build dependency edges
        for module in self.modules.values():
            for dep in module.dependencies:
                if dep in self.modules:
                    self.graph.add_edge(module.name, dep)

        return {
            'total_modules': len(self.modules),
            'tiers': {
                name: {
                    'count': len(tier.modules),
                    'modules': [m.name for m in tier.modules]
                }
                for name, tier in self.TIERS.items()
            },
            'dependency_count': self.graph.number_of_edges(),
            'cyclic_dependencies': len(list(nx.simple_cycles(self.graph))),
        }

    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram syntax"""
        lines = ['graph TB']

        # Define tiers as subgraphs
        for tier_name, tier in self.TIERS.items():
            if tier.modules:
                lines.append(f'  subgraph {tier.name}')
                for module in tier.modules:
                    lines.append(f'    {module.name}[{module.name}]')
                lines.append('  end')

        # Add dependencies
        for source, target in self.graph.edges():
            lines.append(f'  {source} --> {target}')

        return '\n'.join(lines)

    def generate_d3_json(self) -> Dict:
        """Generate D3.js force-directed graph data"""
        nodes = []
        links = []

        for module in self.modules.values():
            nodes.append({
                'id': module.name,
                'group': module.tier,
                'file': module.file_path,
                'functions': len(module.functions),
                'classes': len(module.classes),
            })

        for source, target in self.graph.edges():
            links.append({
                'source': source,
                'target': target,
            })

        return {
            'nodes': nodes,
            'links': links,
            'tiers': {
                name: {
                    'color': tier.color,
                    'description': tier.description
                }
                for name, tier in self.TIERS.items()
            }
        }

    def generate_plantuml(self) -> str:
        """Generate PlantUML component diagram"""
        lines = ['@startuml', '']

        # Define components by tier
        for tier_name, tier in self.TIERS.items():
            if tier.modules:
                lines.append(f'package "{tier.name}" #{tier.color[1:]} {{')
                for module in tier.modules:
                    lines.append(f'  [{module.name}]')
                lines.append('}')
                lines.append('')

        # Add dependencies
        for source, target in self.graph.edges():
            lines.append(f'[{source}] --> [{target}]')

        lines.append('@enduml')
        return '\n'.join(lines)

    def calculate_metrics(self) -> Dict:
        """Calculate architecture metrics"""
        return {
            'modularity': nx.algorithms.community.modularity(
                self.graph,
                nx.algorithms.community.greedy_modularity_communities(self.graph.to_undirected())
            ),
            'average_degree': sum(dict(self.graph.degree()).values()) / len(self.graph.nodes()),
            'density': nx.density(self.graph),
            'strongly_connected_components': nx.number_strongly_connected_components(self.graph),
            'tier_distribution': {
                tier: len(self.TIERS[tier].modules)
                for tier in self.TIERS
            }
        }
```

**API Integration**:
```python
# In src/api/main.py

@app.post("/api/analysis/diagram")
async def generate_diagram(request: AnalysisRequest):
    """
    Generate interactive architecture diagram

    Returns diagram in multiple formats
    """
    # Clone and filter repository
    repo_path = clone_repository(request.repo_url, request.branch)
    filtered_files = filter_repository_files(repo_path, config_path)

    # Generate diagram
    generator = DiagramGenerator(repo_path)
    analysis = generator.analyze_repository(filtered_files)

    return {
        "analysis": analysis,
        "metrics": generator.calculate_metrics(),
        "diagrams": {
            "mermaid": generator.generate_mermaid(),
            "d3": generator.generate_d3_json(),
            "plantuml": generator.generate_plantuml(),
        },
        "download_urls": {
            "svg": f"/api/diagrams/{analysis_id}/download?format=svg",
            "png": f"/api/diagrams/{analysis_id}/download?format=png",
            "json": f"/api/diagrams/{analysis_id}/download?format=json",
        }
    }
```

**UI Component**:
```typescript
// components/ArchitectureDiagram.tsx

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export function ArchitectureDiagram({ data }) {
  const svgRef = useRef();

  useEffect(() => {
    const svg = d3.select(svgRef.current);

    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links).id(d => d.id))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(400, 300))
      .force('collision', d3.forceCollide().radius(30));

    // Draw links
    const link = svg.append('g')
      .selectAll('line')
      .data(data.links)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6);

    // Draw nodes
    const node = svg.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .enter().append('circle')
      .attr('r', d => 5 + d.functions + d.classes)
      .attr('fill', d => data.tiers[d.group].color)
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    // Add labels
    const label = svg.append('g')
      .selectAll('text')
      .data(data.nodes)
      .enter().append('text')
      .text(d => d.id)
      .attr('font-size', 10)
      .attr('dx', 12)
      .attr('dy', 4);

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

      label
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });

    // Drag functions
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  }, [data]);

  return (
    <div className="diagram-container">
      <svg ref={svgRef} width={800} height={600} />
      <div className="legend">
        {Object.entries(data.tiers).map(([name, tier]) => (
          <div key={name} className="legend-item">
            <span
              className="color-box"
              style={{ backgroundColor: tier.color }}
            />
            <span>{name}: {tier.description}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Phase 2: Persistence & Scalability

### 2.1 PostgreSQL Database Integration
- Persist analysis results beyond in-memory storage
- Store historical analysis data
- Track repository changes over time
- Compare analyses across commits

### 2.2 Redis Job Queue
- Background processing for long-running analyses
- Handle concurrent analysis requests
- Job prioritization and scheduling
- Retry failed analyses automatically

### 2.3 WebSocket Progress Updates
- Real-time progress notifications
- Live streaming of findings as they're discovered
- No more polling for status updates

---

## Phase 3: Advanced Features

### 3.1 Custom Rules Engine
- User-defined code review rules
- Company-specific style guides
- Project-specific conventions
- Rule marketplace/sharing

### 3.2 Multi-Repository Analysis
- Analyze entire organizations
- Cross-repository dependency tracking
- Monorepo support
- Microservice architecture analysis

### 3.3 GitHub Issue Integration
- Automatically create GitHub issues from findings
- Link findings to existing issues
- Track resolution progress
- PR comment integration

### 3.4 Trend Analysis
- Track code quality over time
- Identify improving/declining areas
- Team productivity metrics
- Technical debt visualization

---

## Implementation Priority

1. **Immediate (Next Sprint)**:
   - Cost Estimator (prevent surprise bills)
   - PostgreSQL Database (persist results)

2. **Short Term (2-4 weeks)**:
   - Code Diagram Generator (visualize architecture)
   - WebSocket Progress (better UX)

3. **Medium Term (1-2 months)**:
   - Custom Rules Engine
   - GitHub Issue Integration

4. **Long Term (3+ months)**:
   - Multi-Repository Analysis
   - Trend Analysis Dashboard

---

## Cost Estimate Example

**For a typical medium-sized repository**:

```
Repository: SQLExtract (27 Python files)
Total Characters: 125,000
Estimated Tokens: ~31,000 input + ~7,750 output

Cost with GPT-4o-mini:
  Input: 31,000 tokens × $0.150 / 1M = $0.00465
  Output: 7,750 tokens × $0.600 / 1M = $0.00465
  Total: $0.0093 (~$0.01)

Cost with GPT-4o (2x gpt-4o-mini pricing):
  Total: $0.0186 (~$0.02)
```

**Note**: Actual pricing uses 2x GPT-4o-mini as the baseline for calculations.
