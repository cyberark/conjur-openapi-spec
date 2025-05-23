/*
 * Conjur
 *
 * This is an API definition for CyberArk Conjur OSS. You can find out more at [Conjur.org](https://www.conjur.org/).
 *
 * The version of the OpenAPI document: 5.1.0
 * Contact: conj_maintainers@cyberark.com
 * Generated by: https://github.com/openapitools/openapi-generator.git
 */

using System;
using System.Net;
using System.IO;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Reflection;
using RestSharp;
using Xunit;

using Org.OpenAPITools.Client;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Model;

namespace Org.OpenAPITools.Test
{
    /// <summary>
    ///  Class for testing AuthenticationApi
    /// </summary>
    /// <remarks>
    /// This file is automatically generated by OpenAPI Generator (https://openapi-generator.tech).
    /// Please update the test case below to test the API endpoint.
    /// </remarks>
    public class AuthenticationApiTests : IDisposable
    {
        private AuthenticationApi instance;
        private AuthenticationApi nonAuthInstance;
        private Configuration config;

        private string APIKey;
        private string account;
        private string login;

        public AuthenticationApiTests()
        {
            APIKey = Environment.GetEnvironmentVariable("CONJUR_AUTHN_API_KEY");
            account = Environment.GetEnvironmentVariable("CONJUR_ACCOUNT");
            login = Environment.GetEnvironmentVariable("CONJUR_AUTHN_LOGIN");

            Dictionary<string, string> APIPrefix = new Dictionary<string, string>();
            APIPrefix.Add("Authorization", "Token");
            config = new Configuration(
                new Dictionary<string, string>(),
                new Dictionary<string, string>(),
                APIPrefix,
                Environment.GetEnvironmentVariable("CONJUR_HTTP_APPLIANCE_URL")
            );
            config.Username = "admin";
            config.Password = APIKey;

            instance = new AuthenticationApi(config);
            nonAuthInstance = new AuthenticationApi(config);

            ApiResponse<string> res = instance.GetAccessTokenWithHttpInfo(account, login, APIKey, "base64");
            Dictionary<string, string> APIToken = new Dictionary<string, string>();
            APIToken.Add("Authorization", $"token=\"{res.RawContent}\"");

            config.ApiKey = APIToken;
            instance.Configuration = config;
        }

        public void Dispose() { }

        /// <summary>
        /// Test Authenticate
        /// </summary>
        [Fact]
        public void GetAccessTokenTest()
        {
            ApiResponse<string> res = nonAuthInstance.GetAccessTokenWithHttpInfo("dev", "admin", APIKey, "base64");
            Assert.Equal(HttpStatusCode.OK, res.StatusCode);
        }

        /// <summary>
        /// Test Login
        /// </summary>
        [Fact]
        public void GetAPIKeyTest()
        {
            string APIKey = System.Environment.GetEnvironmentVariable("CONJUR_AUTHN_API_KEY");
            ApiResponse<string> response = nonAuthInstance.GetAPIKeyWithHttpInfo("dev");
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        }

        /// <summary>
        /// Test SetPassword
        /// </summary>
        [Fact]
        public void ChangePasswordTest()
        {
            // file deepcode ignore NoHardcodedCredentials/test: This is a test file
            string newPassword = "TestPassword@123";
            var response = instance.ChangePasswordWithHttpInfo(account, newPassword);
            Assert.Equal(HttpStatusCode.NoContent, response.StatusCode);

            // Update the config password
            config.Password = newPassword;
            instance.Configuration = config;

            // Check that we can login with the new password
            instance.GetAPIKey(account);
        }

        /// <summary>
        /// Test UpdateAuthenticatorConfig
        /// </summary>
        [Fact]
        public void EnableAuthenticatorServiceTest()
        {
            var response = instance.EnableAuthenticatorInstanceWithHttpInfo(ServiceAuthenticators.Ldap, "test", account, enabled: true);
            Assert.Equal(HttpStatusCode.NoContent, response.StatusCode);
        }

    }

}
