---
name: setup
description: Nastavení vzdáleného připojení CIAD pro OpenAI a Anthropic a ověření vlastního pracovního prostoru.
---

MCP endpoint je `https://mcp.ciad.cz/mcp`. Použij standardní přihlášení OAuth nabízené hostitelskou aplikací. Přístupový kód se zadává pouze na přihlašovací stránce CIADu, nikdy do chatu, příkazu, konfigurace pluginu ani ticketu podpory.

Pokud účet dosud není aktivní, postupuj podle `https://mcp.ciad.cz/onboarding` nebo kontaktuj `office@ciad.cz`. Kód a synchronizační přístup vydává oprávněný operátor CIADu.

Po přihlášení ověř `list_workspace_files`. Ukaž klientovi dostupné soubory a účel jednotlivých nástrojů. CIAD ukládá výslovně poskytnuté pracovní soubory na své infrastruktuře; jeho oprávnění operátoři k nim mají přístup pro správu a zlepšování. Lokální synchronizace vybraných složek je samostatná a její rozsah je viditelný v konfiguraci. Tento plugin nesbírá historii ani paměť účtů poskytovatele.

Vysvětli `https://mcp.ciad.cz/privacy` a `https://mcp.ciad.cz/terms` věcně, bez tvrzení, že data nikdy neopouštějí klientovo zařízení. Soubory jsou poskytovateli modelu předány pouze při konkrétním použití čtecího nástroje.
