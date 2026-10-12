# CIAD · MCP konektor a AI pracovní prostor

CIAD propojí přihlášený pracovní prostor s OpenAI a Anthropicem. Zpřístupní seznam vybraných pracovních souborů, obsah konkrétního souboru a souhrn poskytnutých provozních metrik. Dále vyhledá české právnické osoby v ARES, zobrazí údaje z obchodního a insolvenčního rejstříku a ověřené části AI Act.

## Připojení

MCP endpoint: **https://mcp.ciad.cz/mcp**. Přihlášení používá OAuth s PKCE. Účet a soukromý přístupový kód vydává CIAD; kód zadávejte pouze na přihlašovací stránce, nikdy do chatu. Vlastní připojení nevyžaduje zveřejnění v katalogu, jeho dostupnost závisí na plánu a nastavení hostitelské aplikace.

Pro Claude Code je připraven `.mcp.json` a `.claude-plugin/plugin.json`, pro Codex a ChatGPT `plugin.json` a `mcp.json`. Skills popisují práci s dostupnými nástroji. Plugin neobsahuje spustitelné skripty ani lifecycle hooks; navazuje pouze vzdálené HTTPS připojení.

Instalace v Claude Code 2.1.281 nebo novějším:

```text
/plugin install ciad --marketplace filipdopita-tech/ciad-connectors
```

V Codexu přidejte GitHub marketplace `filipdopita-tech/ciad-connectors` a nainstalujte `ciad@ciad`. V ChatGPT a Claude lze také přidat vlastní MCP adresu přímo podle návodu výše. Instalace pluginu a OAuth přihlášení jsou samostatné kroky.

Claude manifest nastavuje zobrazované jméno `CIAD`, ikonu a odkazy na dokumentaci, podporu, ochranu dat a podmínky. Pole pro katalog jsou součástí manifestu; jejich validaci bez varování podporuje Claude Code 2.1.281 nebo novější. [Oficiální reference manifestu](https://code.claude.com/docs/en/plugins-reference#directory-listing-fields).

## První ověření

Po OAuth požádejte o seznam pracovních souborů. Zvolte konkrétní cestu ze seznamu a požádejte o její přečtení; zkontrolujte, zda odpověď není zkrácená (`truncated`). Prázdný seznam znamená, že prostor zatím nemá připravené podklady. Provozní souhrn obsahuje jen metriky předané do CIAD; nulový součet nedokládá nulové náklady celého účtu. Úspěšná instalace nebo přihlášení samy neověřují čtení souboru.

Hostovaná služba má 11 nástrojů. Samostatný lokální server pro vývoj má osm nástrojů bez pracovního prostoru; tento plugin se i při instalaci z místního marketplace připojuje k hostované HTTPS službě.

## Data a správa

Vybrané podklady se ukládají na infrastruktuře CIADu. Přidělení specialisté CIAD mohou tyto soubory ručně číst a upravovat, změny mají historii a audit. Katalogové MCP nástroje jsou pro pracovní soubory pouze čtecí; samostatný nástroj `send_feedback` ukládá zpětnou vazbu. Klientské identity se nemohou dostat do prostorů jiné organizace.

Samostatná místní synchronizace se nastavuje výslovným výběrem pracovních složek. Její konfigurace a token se nedistribuují v tomto pluginu. Nepřenášíme automaticky historii, paměť ani přihlašovací údaje účtů ChatGPT/Claude; nepřeprodáváme předplatné poskytovatelů.

[Začít](https://mcp.ciad.cz/onboarding) · [Dokumentace](https://mcp.ciad.cz/docs) · [Ochrana dat](https://mcp.ciad.cz/privacy) · [Podmínky](https://mcp.ciad.cz/terms) · [Podpora](https://mcp.ciad.cz/support). Provozovatel: Český Institut pro AI a Data z.ú., IČO 29752736, office@ciad.cz.

Pluginové texty a manifesty jsou pod licencí MIT. Serverový kód a klientská data nejsou součástí veřejného balíčku. Verze 0.2.2; žádné tvrzení o partnerství s OpenAI či Anthropicem. Zveřejnění v katalogu má samostatný schvalovací proces u poskytovatele.
