/*
 * Conjur
 * This is an API definition for CyberArk Conjur OSS. You can find out more at [Conjur.org](https://www.conjur.org/).
 *
 * The version of the OpenAPI document: 5.1.0
 * Contact: conj_maintainers@cyberark.com
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


package org.conjur.sdk.api;

import org.conjur.sdk.*;
import org.conjur.sdk.auth.*;
import org.conjur.sdk.model.ServiceAuthenticators;
import org.junit.Test;
import org.junit.Before;
import org.junit.After;
import org.junit.Ignore;
import org.junit.Assert;

import com.google.gson.Gson;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.conjur.sdk.api.Utils;

/**
 * API tests for AuthenticationApi
 */
public class AuthenticationApiTest {

    private AuthenticationApi api;
    private ApiClient client = Configuration.getDefaultApiClient();
    private String login = System.getenv().get("CONJUR_AUTHN_LOGIN");
    private String account = System.getenv().get("CONJUR_ACCOUNT");
    private HttpBasicAuth basicAuth;


    @Before
    public void setUp() {
        api = new AuthenticationApi();
        client.setBasePath("http://conjur");
        basicAuth = (HttpBasicAuth) client.getAuthentication("basicAuth");
        basicAuth.setUsername(login);
        basicAuth.setPassword(apiKey());
    }

    @After
    public void tearDown() {
        basicAuth = (HttpBasicAuth) client.getAuthentication("basicAuth");
        basicAuth.setUsername(login);
        basicAuth.setPassword(apiKey());
    }

    public String apiKey(){
        return System.getenv("CONJUR_AUTHN_API_KEY");
    }
    
    /**
     * Test changing a user’s password.
     *
     * @throws ApiException
     *          if the Api call fails
     */
    @Test
    public void changePasswordTest() throws ApiException {
        String newPassword = "@Sup3rS3cr3t@";
        String xRequestId = null;
        api.changePassword(account, newPassword, xRequestId);

        basicAuth.setPassword(newPassword);
        ApiResponse<String> response = api.getAPIKeyWithHttpInfo(account, xRequestId);
        Assert.assertEquals(response.getStatusCode(), 200);
    }

    /**
     * Tests getting the API key of a user given the username and password via HTTP Basic Authentication. 
     *
     * @throws ApiException
     *          if the Api call fails
     */
    @Test
    public void getAPIKeyTest() throws ApiException {
        String response = api.getAPIKey(account, null);

        Assert.assertEquals(response, apiKey());
    }

    /**
     * Tests getting an API token for a given user
     *
     * @throws ApiException
     *          if the Api call fails
     */
    @Test
    public void getAccessToken() throws ApiException {
        String xRequestId = null;
        String encoding = null;
        String response = api.getAccessToken(account, login, apiKey(), encoding, xRequestId);

        String[] keys = { "protected", "payload", "signature" };
        Gson gson = new Gson();
        Map<?, ?> map = gson.fromJson(response, Map.class);

        for (int i = 0; i < keys.length; i++){
            Assert.assertTrue(map.keySet().contains(keys[i]));
        }
    }

    /**
     * Tests rotating the current role's api key
     *
     * @throws ApiException
     *          if the api call fails
     */
    @Test
    public void rotateApiKeyTest() throws ApiException {
        String xRequestId = null;
        String role = null;
        
        String response = api.rotateApiKey(account, role, xRequestId);
        Utils.setEnv("CONJUR_AUTHN_API_KEY", response);
    }
}