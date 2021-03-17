# Using the OpenAPI Spec with Postman

## 1. Start a local Conjur server

Use the provided script `bin/start_conjur`.

## 2. Setup Postman environment

Use the provided script, using the flag to set collection variables based on authentication
credentials for the project's development environment:

```
bin/generate_postman_collection --fill-env-vars
```

This script generates a Postman Collection, and makes a few usability improvements,
including adding Collection variables with Conjur authentication credentials and other
project-wide default values:

| Name              | Initial Value             |
|-------------------|---------------------------|
| `baseUrl`         | `http://localhost:80`     |
| `account`         | `dev`                     |
| `default-auth`    | `authn`                   |
| `role`            | `admin`                   |
| `api-key`         | Retrieved on setup        |
| `token`           | Retrieved on setup        |
| `formatted-token` | `Token token="{{token}}"` |

In Postman, variables are used by referencing the variable name in `{{doubleBraces}}`.
This convention is also used in [Step 4](#4-make-a-request) when using variable values to
construct API requests.

Setup also includes a [pre-request script](https://learning.postman.com/docs/writing-scripts/pre-request-scripts/)
that will refresh the access token before each API call through Postman. This script makes
an API call to Conjur's `authenticate` endpoint, and stores the results under the `token` Collection
variable.

## 3. Import the collection into Postman

The generated collection is saved under `out/postman/collection.json`.

Postman documentation for importing a collection is found
[here](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-postman-data).

## 4. Make a request

This example will detail using Postman to make requests to set and then fetch
a variable in Conjur, `dev:variable:testSecret`.

Details on required and optional request parameters are defined in the documentation.
Postman's `Documentation` tab will present endpoint documentation alongside its interactive
window, which is helpful in constructing valid requests.

Requests in the Conjur collection are grouped by `tag`. Requests for updating and
retrieving secrets can be found in the `secrets` directory.

### Making a POST Request

As defined in the Conjur docs, a POST request to the `/secrets/:account/:kind/:identifier`
endpoint requires its path parameters and prospective variable value as the request body.
The following configuration will allow for a successful request:

Path Variables
| Key        | Value         |
|------------|---------------|
| account    | `{{account}}` |
| kind       | `variable`    |
| identifier | `testSecret`  |

Authorization
| Type    | Key           | Value                 | Add to |
|---------|---------------|-----------------------|--------|
| API Key | Authorization | `{{formatted_token}}` | Header |


Body
| Type  | Content        |
|-------|----------------|
| `raw` | `Hello World!` |

Sending this request will result in a `201 Created` response, with an empty response body.
This can be verified with a request to retrieve the value of `testSecret`.

### Making a GET Request

The GET request to `/secrets/:account/:kind/:identifier` is in the same directory.
It uses the same configuration as the POST request, without the body contents.
This request will result in a `200 OK` response, with the the response body presented:

```
Hello World!
```