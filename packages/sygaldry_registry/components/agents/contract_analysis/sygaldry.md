# Contract Analysis Agent

## Overview

The Contract Analysis Agent is a sophisticated legal document analysis tool that uses LLMs to identify risks, obligations, and key terms in contracts. It provides comprehensive contract review with actionable insights and recommendations.

## Features

- **Key Term Extraction**: Identifies and categorizes important contract clauses
- **Risk Assessment**: Evaluates financial, legal, operational, and reputational risks
- **Obligation Tracking**: Extracts all contractual obligations with party assignments
- **Clause Categorization**: Automatically classifies clauses by type and importance
- **Red Flag Detection**: Highlights concerning or unusual contract terms
- **Executive Summaries**: Generates business-focused summaries for stakeholders
- **Actionable Recommendations**: Provides specific suggestions for contract review
- **Multi-Contract Support**: Works with various contract types (employment, licenses, services, etc.)

## Installation

```bash
sygaldry add contract_analysis_agent
```

## Quick Start

```python
import asyncio
from contract_analysis import analyze_contract

async def main():
    contract_text = """
    Your contract text here...
    """

    result = await analyze_contract(
        contract_text=contract_text,
        analysis_focus=['risks', 'obligations'],
        include_recommendations=True
    )

    print(f"Overall Assessment: {result.overall_assessment}")
    print(f"Risks Found: {len(result.risks)}")
    print(f"Obligations: {len(result.obligations)}")

asyncio.run(main())
```

## Core Functions

### `analyze_contract()`

Main function for comprehensive contract analysis.

**Parameters:**
- `contract_text` (str): Full text of the contract to analyze
- `analysis_focus` (list[str] | None): Specific areas to focus on
  - Options: 'risks', 'obligations', 'key_terms', 'payments', 'termination', 'liabilities', etc.
- `include_recommendations` (bool): Whether to include actionable recommendations (default: True)
- `llm_provider` (str): LLM provider to use (default: "openai")
- `model` (str): Specific model to use (default: "gpt-4o-mini")

**Returns:** `ContractAnalysisResult`

**Example:**
```python
result = await analyze_contract(
    contract_text=my_contract,
    analysis_focus=['risks', 'liabilities', 'termination'],
    include_recommendations=True
)

# Access results
print(result.contract_type)
print(result.overall_assessment)
for risk in result.risks:
    if risk.severity == 'critical':
        print(f"Critical Risk: {risk.description}")
```

### `quick_risk_check()`

Fast risk assessment without full analysis.

**Parameters:**
- `contract_text` (str): Contract text to assess

**Returns:** Dictionary with simplified risk information

**Example:**
```python
risk_info = await quick_risk_check(contract_text)
print(f"Overall Risk: {risk_info['overall_risk']}")
print(f"Critical Risks: {risk_info['critical_risks']}")
```

### `extract_obligations_only()`

Extract only obligations without full analysis.

**Parameters:**
- `contract_text` (str): Contract text to process

**Returns:** List of simplified obligation dictionaries

**Example:**
```python
obligations = await extract_obligations_only(contract_text)
for ob in obligations:
    print(f"{ob['party']}: {ob['description']} (Due: {ob['deadline']})")
```

## Response Models

### ContractAnalysisResult

Complete analysis result with all findings.

**Fields:**
- `key_terms` (list[ContractClause]): Important contract clauses
- `risks` (list[RiskAssessment]): Identified risks
- `obligations` (list[ContractObligation]): Contractual obligations
- `summary` (str): Executive summary
- `recommendations` (list[str]): Actionable recommendations
- `overall_assessment` (str): Overall contract assessment
  - Values: 'favorable', 'neutral', 'unfavorable', 'requires_legal_review'
- `contract_type` (str): Type of contract
- `parties` (list[str]): Contract parties

### ContractClause

Individual contract clause information.

**Fields:**
- `clause_type` (str): Type (e.g., 'termination', 'liability', 'payment')
- `content` (str): Actual clause text
- `section` (str): Section reference
- `importance` (str): Importance level ('low', 'medium', 'high', 'critical')
- `explanation` (str): Plain language explanation

### RiskAssessment

Risk evaluation details.

**Fields:**
- `risk_type` (str): Type (e.g., 'financial', 'legal', 'operational')
- `severity` (str): Severity level ('low', 'medium', 'high', 'critical')
- `description` (str): Risk description
- `affected_clause` (str): Which clause creates the risk
- `mitigation_suggestion` (str): How to mitigate
- `likelihood` (str): Likelihood of occurrence

### ContractObligation

Contractual obligation details.

**Fields:**
- `party` (str): Responsible party
- `obligation_type` (str): Type (e.g., 'payment', 'delivery', 'reporting')
- `description` (str): What must be done
- `deadline` (str | None): Deadline or timeline
- `consequences` (str): Consequences of non-compliance
- `recurring` (bool): One-time or recurring

## Use Cases

### 1. Employment Agreement Review

```python
employment_contract = """
EMPLOYMENT AGREEMENT
...
"""

result = await analyze_contract(
    contract_text=employment_contract,
    analysis_focus=['compensation', 'termination', 'non_compete', 'benefits']
)

# Check for problematic clauses
for risk in result.risks:
    if 'non-compete' in risk.affected_clause.lower():
        print(f"Non-compete risk: {risk.description}")
```

### 2. Software License Assessment

```python
license_agreement = """
SOFTWARE LICENSE AGREEMENT
...
"""

result = await analyze_contract(
    contract_text=license_agreement,
    analysis_focus=['liabilities', 'renewal_terms', 'fees', 'termination']
)

# Check liability caps
for clause in result.key_terms:
    if clause.clause_type == 'liability':
        print(f"Liability terms: {clause.explanation}")
```

### 3. Service Contract Analysis

```python
service_contract = """
PROFESSIONAL SERVICES AGREEMENT
...
"""

result = await analyze_contract(
    contract_text=service_contract,
    analysis_focus=['deliverables', 'payments', 'warranties', 'IP_rights']
)

# Review obligations by party
for ob in result.obligations:
    print(f"{ob.party} must: {ob.description}")
```

### 4. Quick Risk Screening

```python
# For rapid assessment of multiple contracts
contracts_to_review = [contract1, contract2, contract3]

for i, contract in enumerate(contracts_to_review):
    risk_check = await quick_risk_check(contract)
    if risk_check['overall_risk'] in ['unfavorable', 'requires_legal_review']:
        print(f"Contract {i+1} requires detailed review")
        print(f"Critical risks: {risk_check['critical_risks']}")
```

## Recognized Contract Types

The agent automatically identifies and handles:

- Employment Agreements
- Software License Agreements (SaaS, perpetual, etc.)
- Service Agreements
- Non-Disclosure Agreements (NDAs)
- Consulting Agreements
- Partnership Agreements
- Lease Agreements
- Purchase Agreements
- Master Service Agreements (MSAs)
- Vendor Contracts
- Franchise Agreements
- Distribution Agreements

## Identified Clause Types

The agent recognizes and categorizes:

- **Payment Terms**: Compensation, fees, payment schedules
- **Termination**: Termination conditions, notice periods
- **Liability**: Liability limitations, indemnification
- **Confidentiality**: NDA provisions, data protection
- **Non-Compete**: Restrictive covenants
- **Intellectual Property**: IP ownership, licensing
- **Warranties**: Representations and warranties
- **Dispute Resolution**: Arbitration, mediation, jurisdiction
- **Renewal**: Auto-renewal, extension terms
- **Insurance**: Insurance requirements
- **Audit Rights**: Right to audit provisions
- **Force Majeure**: Exceptional circumstances

## Best Practices

1. **Focus Your Analysis**: Use `analysis_focus` to target specific concerns
2. **Review Recommendations**: Pay attention to the recommendations list
3. **Check Red Flags**: Always review items in the red_flags list
4. **Verify Critical Obligations**: Track obligations marked as critical
5. **Compare Risk Levels**: Use severity and likelihood together for priority
6. **Legal Review**: Always get legal review for high-risk or critical contracts
7. **Structured Workflow**: Use quick_risk_check for screening, full analysis for important contracts

## Limitations

- This agent provides analysis assistance but is NOT a substitute for professional legal advice
- Always have important contracts reviewed by qualified legal counsel
- The agent may not catch all nuanced legal issues
- Analysis quality depends on contract clarity and completeness
- Regional legal variations may not be fully captured

## Environment Variables

Set at least one provider's API key:

```bash
export OPENAI_API_KEY="your-openai-key"
# OR
export ANTHROPIC_API_KEY="your-anthropic-key"
```

## Advanced Configuration

### Custom Model Selection

```python
# Use Claude for analysis
result = await analyze_contract(
    contract_text=contract,
    llm_provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Targeted Analysis

```python
# Focus only on financial and termination risks
result = await analyze_contract(
    contract_text=contract,
    analysis_focus=['payment', 'fees', 'penalties', 'termination', 'cancellation'],
    include_recommendations=True
)
```

## Integration with Lilypad

This agent supports Lilypad for observability:

```python
from lilypad import configure_lilypad

configure_lilypad(project_name="contract-review")

# Analysis will be automatically traced
result = await analyze_contract(contract_text)
```

## Version History

- **0.1.0** (2024): Initial release with core functionality

## License

MIT License - see LICENSE file for details

## Support

For issues, feature requests, or questions:
- GitHub: https://github.com/greyhaven-ai/sygaldry/issues
- Documentation: https://sygaldry.ai/docs/agents/contract-analysis
