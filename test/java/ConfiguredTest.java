package org.conjur.sdk.api;

import org.conjur.sdk.*;
import org.conjur.sdk.auth.*;
import org.junit.*;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.io.*;

public class ConfiguredTest {
    protected ApiClient client;
    protected String login;
    protected String account;
    protected HttpBasicAuth basicAuth;
    protected ApiKeyAuth conjurAuth;

    private static final String OIDC_POLICY_FILE = "/config/oidc-webservice.yml";
    private static final String DEFAULT_POLICY_FILE = "/config/policy.yaml";

    private static void setupAccessToken(String apiKey) throws ApiException {
        String account = System.getenv("CONJUR_ACCOUNT");
        String login = System.getenv("CONJUR_AUTHN_LOGIN");
        ApiClient client = Configuration.getDefaultApiClient();
        AuthenticationApi authApi = new AuthenticationApi();
        String apiToken = authApi.getAccessToken(account, login, apiKey, "base64", null);
        ApiKeyAuth conjurAuth = (ApiKeyAuth) client.getAuthentication("conjurAuth");
        conjurAuth.setApiKeyPrefix("Token");
        conjurAuth.setApiKey(String.format("token=\"%s\"", apiToken));
    }

    private static void setupClientAuth() throws ApiException {
        String apiKey = System.getenv("CONJUR_AUTHN_API_KEY");
        ApiClient client = Configuration.getDefaultApiClient();
        String login = System.getenv("CONJUR_AUTHN_LOGIN");
        HttpBasicAuth basicAuth = (HttpBasicAuth) client.getAuthentication("basicAuth");
        basicAuth.setUsername(login);
        basicAuth.setPassword(apiKey);
        
        setupAccessToken(apiKey);
    }

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

    @AfterClass
    public static void loadDefaultPolicy() throws ApiException, IOException {
        PoliciesApi policiesApi = new PoliciesApi();
        List<String> lines = Files.readAllLines(Paths.get(DEFAULT_POLICY_FILE));
        String policyText = String.join(System.lineSeparator(), lines);
        policiesApi.replacePolicy(System.getenv("CONJUR_ACCOUNT"), "root", policyText, null);
    }

    @BeforeClass
    public static void setUpClass() throws ApiException{
        ApiClient client = Configuration.getDefaultApiClient();
        client.setSslCaCert(client.getCertInputStream());
        setupClientAuth();
    }

    @Before
    public void setUp() throws ApiException, IOException {
        client = Configuration.getDefaultApiClient();
        basicAuth = (HttpBasicAuth) client.getAuthentication("basicAuth");
        conjurAuth = (ApiKeyAuth) client.getAuthentication("conjurAuth");
        login = System.getenv("CONJUR_AUTHN_LOGIN");
        account = System.getenv("CONJUR_ACCOUNT");

        setupClientAuth();
    }
}
