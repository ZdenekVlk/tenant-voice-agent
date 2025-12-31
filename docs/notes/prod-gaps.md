# Šablona
## [AREA] Krátký název
**Dev stav:** co je dnes  
**Prod cíl:** jak to má být v produkci  
**Riziko:** co se může stát, když to necháš jak je  
**Fix (konkrétně):** 2–5 bodů co udělat  
**Kde v kódu:** soubory / moduly  
**Kdy:** M2 / před launch / později  
**Owner:** ty / CODEX


# Poznámky

## [CORS] Dev wildcard → prod allowlist
**Dev stav:** CORS je permissive (povoluje localhost, případně "*").
**Prod cíl:** Povolit jen originy/domény, které jsou přiřazené tenantovi.
**Riziko:** kdokoliv může volat API z libovolné stránky; zneužití endpointů.
**Fix (konkrétně):**
- Zpřísnit CORS: allowlist, metody, headers.
- Napojit allowlist na `tenant_domains` (nebo globální allowlist).
- Ošetřit preflight a `Authorization` header.
**Kde v kódu:** backend app init (CORS middleware), origin normalizace, tenant lookup.
**Kdy:** M2 / před produkčním embedem.
**Owner:** CODEX
