package org.conjur.sdk.api;

import org.conjur.sdk.*;
import org.conjur.sdk.auth.*;
import org.junit.*;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

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

    private static final String OIDC_POLICY_FILE = "/config/oidc-webservice.yml";
    public void setupOIDCWebservice() throws ApiException {
        PoliciesApi policiesApi = new PoliciesApi();
        SecretsApi secretsApi = new SecretsApi();
        try {
            List<String> lines = Files.readAllLines(Paths.get(OIDC_POLICY_FILE));
            String policyText = String.join(System.lineSeparator(), lines);
            policiesApi.updatePolicy(account, "root", policyText, null);
            secretsApi.createSecret(
                account,
                "variable",
                "conjur/authn-oidc/test/provider-uri",
                null,
                null,
                "https://keycloak:8443/auth/realms/master"
            );

            secretsApi.createSecret(
                account,
                "variable",
                "conjur/authn-oidc/test/id-token-user-property",
                null,
                null,
                "preferred_username"
            );
        } catch (IOException e) {
            Assert.fail("Failed to read OIDC webservice policy file");
        }
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
