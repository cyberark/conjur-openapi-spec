# Interpreting The OpenAPI Specification Files

## Spec file structure

The root spec file is located in `spec/openapi.yml` and has several functions:

* Define components shared between multiple spec files
* Define `tags` which help group API endpoints by common functionality
* Define, through references, all of the API's paths

Each of the other files in the `/spec/` directory define the actual functionality of each path and the components/schemas which are only used in those paths.

#### The $ref keyword

The `$ref` keyword is often used in the Conjur OpenAPI spec in order to reference external YAML objects. This is done in order to reduce duplication and allow the spec to be split across multiple files. The syntax is shown below:

```yaml
$ref: "<file-path>#<object-path>"
```

  `<file-path>`: The relative path of a file to reference. Can be omitted entirely to reference objects in the current file.

  `<object-path>`: A forward slash separated path to the referenced object where `/` is the root of the document.

[`openapi.yml#/components/responses`](https://github.com/cyberark/conjur-openapi-spec/blob/main/spec/openapi.yml#L187):

```yaml
    UnauthorizedError:
      description: "Authentication information is missing or invalid"
```

[`status.yml`](https://github.com/cyberark/conjur-openapi-spec/blob/main/spec/status.yml):

```yaml
components:
  schemas:
    WhoAmI:
      type: object
      description: "Information about the client making a request"
      properties:
        <object properties>
          
  paths:
    WhoAmI:
      get:
        tags:
        - "status"
        summary: "Provides information about the client making an API request."
        description: |
          WhoAmI provides information about the client making an API request.
          It can be used to help troubleshoot configuration by verifying authentication
          and the client IP address for audit and network access restrictions.
          For more information, see Host Attributes.
        operationId: "whoAmI"
        responses:
          "200":
            description: "Details about the client making the request"
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/WhoAmI'
          "401":
            $ref: 'openapi.yml#/components/responses/UnauthorizedError'

        security:
          - conjurAuth: []
```

For the sake of simplicity will refer to sections of the document by their object-path from this point on.

#### /components

This section encompases several subsections which contain different YAML objects to be referenced in other parts of the document. There are many different types of objects you can define here, and a full list is [available](https://swagger.io/docs/specification/components/), however we will mostly focus on `schemas` and `paths` as they are most often used in the Conjur spec. 

##### /components/schemas

```yaml
components:
  schemas:
    ReturnSchema:
      type: object
      properties:
        first:
          type: string
        second:
          type: number
      example: |
        {
          "first": "some string",
          "second": 42
        }
  responses:
    ResponseWithObject:
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/ReturnSchema"
```

A list of all possible schema object fields can be found [here](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md#schema-object). However the following fields are most common in Conjur:

* `type`: Specifies the type of the object (`string`, `number`, `integer`, `boolean`, `array`, `object`)

  * If `type` is `object` you can optionally specify a `properties` field which defines the possible JSON properties. Each of the properties is its own schema (and could technically be a reference to a schema)

* `description`: A *CommonMark* formatted description of the schema

* `example`: An example of the schema to display in documentation

* `enum`: Specifies this schema as an enumeration and lists the possible values

  ```yaml
  components:
    schemas:
      Authenticators:
        type: string
        enum:
        - authn
        - authn-iam
        - authn-oidc
        - authn-ldap
        - authn-k8s
        - authn-gcp
        - authn-azure
  ```

##### /components/paths

This section contains referenceable objects which represent API endpoints. In the Conjur spec each of these is referenced by the main `/paths` section (which actually defines the URI relating to each path).

`openapi.yml`

```yaml
paths:
  '/{authenticator}/{account}/login':
    $ref: 'authentication.yaml#/components/paths/Login'
```

`authentication.yaml`

```yaml
components:
  paths:
    Login:
      get:
        tags:
        - "authn"
        summary: "<short description of the operation>"
        description: "<long description of the operation>"
        operationId: "login"
        parameters:
        - name: "authenticator"
          in: "path"
          description: "The Authenticator"
          required: true
          schema:
            $ref: "#/components/schemas/Authenticators"
          example: "authn"

        - name: "account"
          in: "path"
          description: "Organization account name"
          required: true
          schema:
            $ref: 'openapi.yml#/components/schemas/AccountName'

        responses:
          "200":
            $ref: 'openapi.yml#/components/responses/ApiKey'
          "400":
            $ref: 'openapi.yml#/components/responses/BadRequest'
          "401":
            $ref: 'openapi.yml#/components/responses/UnauthorizedError'
          "422":
            $ref: 'openapi.yml#/components/responses/UnprocessableEntity'
          "500":
            $ref: 'openapi.yml#/components/responses/InternalServerError'

        security:
          - basicAuth: []
```

The path object has optional fields for each of the HTTP methods, these fields separate one URI into several different operations. So even though two operations share the same URI they could have entirely different request/response bodies and query parameters, the only thing they must share are `path` variables. 

A full overview of all path fields can be found [here](https://swagger.io/docs/specification/paths-and-operations/). The following is a breakdown of the most important fields:

* `tags`: This defines how this operation is organized in the generated client, documentation, etc...

  * Possible tags are defined in `openapi.yml#/tags` along with a description of their purpose.
  * The generated clients will *usually* organize operations with the same tag into classes/files together

* `summary`: A abbreviated description of the operation

* `description`: A longer description of the operation. In most generated clients this becomes the docstring for the operation's function.

* `parameters`: A list of all possible parameters for this endpoint, including both path and query parameters

  * The `in` field defines whether the parameter is in the URI `path` or `query`. You can also specify `header` and `cookie` parameters
  * The `required` field determines if this parameter must be present, by default it is `false`. Note that `path` parameters **must** have `required: true`
  * The `schema` field defines the schema which this parameter follows.

* `responses`: Defines the possible return codes for this endpoint along with a description of the returned object

  * A response object must contain a `description` of what the return code means as well as a `content` field describing the response

  ```yaml
  content:    
    responses:
      ApiKey:
        description: "The response body is the API key"
        content:
          text/plain: # This specifies the MIME type of the response
            schema: # specify the schema of the returned object (could be a reference)
              type: string
              example: '14m9cf91wfsesv1kkhevg12cdywm2wvqy6s8sk53z1ngtazp1t9tykc'
  ```

* `security`: Defines the security method for this operation. In the ConjurAPI we either have `conjurAuth` which corresponds to using a Conjur token for authentication, or `basicAuth` which is just basic HTTP authentication.

  * The security field is a list and can be defined in several different ways.

  Either just one security method can be used:

  ```yaml
  security:
    - conjurAuth: []
  ```

  Or you can specify that one of several authentication methods can be chosen:

  ```yaml
  security:
    - conjurAuth: []
    - basicAuth: []
  ```

  Or you can specify that **both** methods should be used

  ```yaml
  security:
    - conjurAuth: []
      basicAuth: []
  ```

  This pattern is used on the `rotateAPIKey` operation, in which `basicAuth` is used to rotate a role's own API key and `conjurAuth` is used to rotate another roles API key

#### /paths

The `/paths` section defines the URI, methods, and request details for each endpoint in the spec. Note that this section is different than the `/components/paths` section, which does not define URI's for the objects, but simply declares path objects that can be referenced using the `$ref` keyword (more on this below). In the Conjur spec this section is composed entirely of references to other documents in which the full path is defined:

`openapi.yml`

```yaml
paths:
  '/{authenticator}/{account}/login':
    $ref: 'authentication#/components/paths/Login'
```

The URI is relative to the base path of the server, and may include variables which are enclosed by braces. Each of these variables will be defined in the referenced object. Note that query variables are always excluded from the URI and instead defined in the object (i.e. `/test?name=alice` is an invalid URI, `name` should be defined in the path object itself).
