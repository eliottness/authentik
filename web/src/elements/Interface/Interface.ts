import { DEFAULT_CONFIG } from "@goauthentik/common/api/config";
import { config, tenant } from "@goauthentik/common/api/config";
import { UIConfig, uiConfig } from "@goauthentik/common/ui/config";
import {
    authentikConfigContext,
    authentikEnterpriseContext,
    authentikTenantContext,
} from "@goauthentik/elements/AuthentikContexts";
import type { AdoptedStyleSheetsElement } from "@goauthentik/elements/types";
import { ensureCSSStyleSheet } from "@goauthentik/elements/utils/ensureCSSStyleSheet";

import { ContextProvider } from "@lit-labs/context";
import { state } from "lit/decorators.js";

import PFBase from "@patternfly/patternfly/patternfly-base.css";

import type { Config, CurrentTenant, LicenseSummary } from "@goauthentik/api";
import { EnterpriseApi, UiThemeEnum } from "@goauthentik/api";

import { AKElement } from "../Base";

type AkInterface = HTMLElement & {
    getTheme: () => Promise<UiThemeEnum>;
    tenant?: CurrentTenant;
    uiConfig?: UIConfig;
    config?: Config;
};

export class Interface extends AKElement implements AkInterface {
    @state()
    uiConfig?: UIConfig;

    _configContext = new ContextProvider(this, {
        context: authentikConfigContext,
        initialValue: undefined,
    });

    _config?: Config;

    @state()
    set config(c: Config) {
        this._config = c;
        this._configContext.setValue(c);
        this.requestUpdate();
    }

    get config(): Config | undefined {
        return this._config;
    }

    _tenantContext = new ContextProvider(this, {
        context: authentikTenantContext,
        initialValue: undefined,
    });

    _tenant?: CurrentTenant;

    @state()
    set tenant(c: CurrentTenant) {
        this._tenant = c;
        this._tenantContext.setValue(c);
        this.requestUpdate();
    }

    get tenant(): CurrentTenant | undefined {
        return this._tenant;
    }

    _licenseSummaryContext = new ContextProvider(this, {
        context: authentikEnterpriseContext,
        initialValue: undefined,
    });

    _licenseSummary?: LicenseSummary;

    @state()
    set licenseSummary(c: LicenseSummary) {
        this._licenseSummary = c;
        this._licenseSummaryContext.setValue(c);
        this.requestUpdate();
    }

    get licenseSummary(): LicenseSummary | undefined {
        return this._licenseSummary;
    }

    constructor() {
        super();
        document.adoptedStyleSheets = [...document.adoptedStyleSheets, ensureCSSStyleSheet(PFBase)];
        tenant().then((tenant) => (this.tenant = tenant));
        config().then((config) => (this.config = config));
        new EnterpriseApi(DEFAULT_CONFIG).enterpriseLicenseSummaryRetrieve().then((enterprise) => {
            this.licenseSummary = enterprise;
        });

        this.dataset.akInterfaceRoot = "true";
    }

    _activateTheme(root: AdoptedStyleSheetsElement, theme: UiThemeEnum): void {
        super._activateTheme(root, theme);
        super._activateTheme(document, theme);
    }

    async getTheme(): Promise<UiThemeEnum> {
        if (!this.uiConfig) {
            this.uiConfig = await uiConfig();
        }
        return this.uiConfig.theme?.base || UiThemeEnum.Automatic;
    }
}
