package org.conjur.sdk.api;

import org.conjur.sdk.*;
import org.conjur.sdk.auth.*;
import org.junit.Before;
import org.junit.After;
import org.junit.BeforeClass;
import org.junit.AfterClass;

public class ConfiguredTest {
    protected ApiClient client;
    protected String login;
    protected String account;
    protected HttpBasicAuth basicAuth;
    protected ApiKeyAuth conjurAuth;

    private void setupAccessToken(String apiKey) throws ApiException {
        AuthenticationApi authApi = new AuthenticationApi();
        String apiToken = authApi.getAccessToken(account, login, apiKey, "base64", null);
        conjurAuth = (ApiKeyAuth) client.getAuthentication("conjurAuth");
        conjurAuth.setApiKeyPrefix("Token");
        conjurAuth.setApiKey(String.format("token=\"%s\"", apiToken));
    }

    private void setupClientAuth() throws ApiException {
        String apiKey = System.getenv("CONJUR_AUTHN_API_KEY");
        basicAuth = (HttpBasicAuth) client.getAuthentication("basicAuth");
        basicAuth.setUsername(login);
        basicAuth.setPassword(apiKey);
        
        setupAccessToken(apiKey);
    }

    @Before
    public void setUp() throws ApiException {
        client = Configuration.getDefaultApiClient();
        login = System.getenv("CONJUR_AUTHN_LOGIN");
        account = System.getenv("CONJUR_ACCOUNT");
        client.setBasePath(System.getenv("CONJUR_HTTP_APPLIANCE_URL"));

        setupClientAuth();
    }
}
