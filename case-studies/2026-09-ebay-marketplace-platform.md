# Case study: eBay's marketplace app platform and developer experience

**Role:** Technical Product Manager, Marketplace App Platform & Developer Experience, eBay (Dec 2019 – Mar 2022, Seattle) · **Type:** career case study. Every fact here comes from the author's published resume. Nothing confidential is included.

## The job

I owned the platform strategy and roadmap that let **third-party sellers, ISVs and internal teams** build on, integrate with and scale on eBay's commerce ecosystem. In a marketplace, the platform's customers are other builders. Their integration cost becomes the marketplace's growth ceiling.

## Results

| Metric | Result |
|---|---|
| Annual cost savings | **$300M+** |
| Platform adoption | **+35%** |
| Integration time for developers | **−40%** |
| Deployment speed | **40% faster** |
| Latency | **30% lower** |
| Availability, seller-facing APIs | **99.9%** |

## Three workstreams

**1. Standardize the contract.** API standardization, self-service onboarding and reusable microservice frameworks, so a seller, an ISV or an internal team integrates against one consistent surface instead of many one-off ones. This drove the $300M+ in annual savings and the 35% adoption growth, and made third-party integrations faster.

**2. Modernize what's behind it.** Moved from monolithic systems to cloud-native microservices: 40% faster deployments, 30% lower latency, and 99.9% availability on the seller-facing APIs that sellers' own businesses depend on.

**3. Make the platform self-serve.** Launched a self-service developer portal, SDK toolkits and sandbox environments. Integration time fell 40% and the developer ecosystem grew.

## How it carries into my AI work

A marketplace platform works when the contract between systems is clear and dependable: the API says what it does, and does what it says. AI agents need exactly that from their tools. That's what [MCP](https://modelcontextprotocol.io) standardizes, and what my [MCP trust tools](https://github.com/vishalhabib99/mcp-trust-check) check (is the tool documented, does it fail safely, is its "success" real).

The same idea applies to AI-generated content. In [listing-claim-check](https://github.com/vishalhabib99/listing-claim-check), the seller's item specifics are the contract, and an AI-written listing is checked against them before a buyer sees it.
