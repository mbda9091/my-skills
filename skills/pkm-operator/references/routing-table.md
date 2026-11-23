# Routing Table

Choose the smallest leaf skill that can satisfy the request.

## Capture

Use `$pkm-capture` when the user wants to:

- save this conversation
- record a prompt/answer
- capture a webpage excerpt or temporary note
- put something into the vault without yet deciding final knowledge value

## Ingress

Use `$pkm-ingress` when an external system, bot, browser tool, CLI, another agent, or user asks to submit outside content into the vault without reading vault rules. This creates an External Drop only.

## Triage

Use `$pkm-triage` when the user asks:

- where should this go?
- is this a Project, Area, Resource, or Archive item?
- should this become a project or just a note?
- clean up inbox routing

## Distill

Use `$pkm-distill` when the user asks:

- extract reusable knowledge
- turn a conversation into a resource note
- summarize into principles, methods, checklists, decisions, or actions
- convert raw material into durable notes

## Link

Use `$pkm-link` when the user asks:

- add backlinks
- update Daily
- update MOC
- connect this note to projects/resources/areas
- add raw/source links

## Ingest

Use `$pkm-ingest` when the user asks to process, normalize, or convert an existing file under `00_inbox/External Drops/` into formal vault notes, tasks, links, or a rejection.

## Review

Use `$pkm-review` when the user asks:

- review inbox
- weekly review
- find unprocessed AI conversations
- find stale projects or weak resources
- suggest next PKM cleanup actions

## Combined Requests

If a user asks for a complete flow, run leaf skills in workflow order:

```text
ingress -> capture -> triage -> distill -> link -> ingest -> review
```

Skip stages that are unnecessary. For example, an AI conversation capture with a clear target can use:

```text
capture -> distill -> link
```
