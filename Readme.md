# Lambda Layers Unleashed: Building Reusable Components for AWS Serverless Applications
![Lambda Layers](/images/Lambda%20Layers.png)

## Table of Contents

- [Introduction](#introduction)
- [Understanding Lambda Layers](#understanding-lambda-layers)
    - [How Layers Work](#How-Layers-Work) 
    - [Layer Versions ](#Layer-Versions) 
    - [Benefits of Using Lambda Layers ](#Benefits-of-Using-Lambda-Layers) 
    - [Common Use Cases for AWS Lambda Layers](#Common-Use-Cases-for-AWS-Lambda-Layers) 
- [Creating Your First Lambda Layer](#creating-your-first-lambda-layer)
    - [Prepare and package your  Lambda layer Content](#Prepare-and-package-your-Lambda-layer-Content)
    - [Create and Publish your Lambda Layer in AWS](#Create-and-Publish-you-Lambda-Layer-in-AWS)
    - [Use the Layer in Your Lambda Function](#Use-the-Layer-in-Your-Lambda-Function)    
- [Advanced Layer Techniques](#advanced-layer-techniques)
  - [Multi-language Layers](#multi-language-layers)
  - [Layer Size Optimization](#layer-size-optimization) 
  - [Automated Layer Updates](#automated-layer-updates)
- [Best Practices for Lambda Layers](#best-practices-for-lambda-layers) 
- [Conclusion](#conclusion)
- [References and Additional Resources](#References-and-Additional-Resources)


## Introduction
Serverless computing is a computing technique and an execution model that enables you to build and run application code without having to think about provisioning and managing servers and/or back-end infrastructure. In AWS Lambda, a serverless service is the backbone when it comes to building serverless applications on AWS. AWS Lambda allows you to focus on your application code while it handles infrastructure management, auto-scaling and other heavy lifting.

As your serverless applications grow in complexity and the number of Lambda functions becomes numerous, certain challenges, such as dependency management and code reuse, are inevitable. To address these issues, our hero , Lambda Layers, comes to the rescue. In this article we will explore everything you need to know about Lambda Layers, from the basics to some advanced concepts.


## Understanding AWS Lambda Layers
A lambda layer is a special container, a `.zip` file archive that contains supplementary code or data. Lambda layers serve as a distribution mechanism for function dependencies, custom runtime, or configuration files for your Lambda functions. Layers let you keep your function deployment packages small and organized by separating your function business logic code from its dependencies.

![Lambda Layer Architecture](/images/layer-example.gif)

In the diagram shown above, using the traditional approach without layers, each of the Lambda functions packages contains everything it needs to function. Lambda Function **A**  includes requests, pyshorteners , qrcode dependencies and custom runtime libraries (logging, authentication), along with its  business logic code, (requests, pyshorteners, qrcode). Function  **B** also uses the same  dependencies and custom runtime libraries, plus its own business logic. With this approach, you can clearly see there is code duplication across the two functions, leading to larger deployment packages.

The optimized approach as shown in the diagram using Lambda Layers showsthat , both functions **A** and **B** now  only contain their business logic code which has much smaller packages and dependencies requests, pyshorteners, qrcode are bundled into a layer. The custom runtime libraries (logging, authentication) are also put in another layer that is shared by both functions.
### How Layers Work

A layer essentially bundles code or data into a `ZIP` archive that is automatically extracted by the lambda service into the `/opt`  directory in your function’s execution environment. Your function code can then access the Layer's content during its execution.

Lambda Layers operate using a simple workflow.
- 1. First, you package your function's, dependencies or shared code into a `ZIP` file.
- 2. You then create and publish the Layer to the  Lambda service.
- 3. After creating the layer, you can attach the layer to one or more lambda functions.
- 4. When your function executes, it can then access the Layer's content as if it were part of the function's deployment package.
- 5. You can then update the layer and create different versions of the layer depending on your needs. 

Lambda allows you to add up to a maximum of five Layers per function, and the layer content still counts towards the function's deployment package size quota (i.e. 250MB for .zip file archives).
**NOTE** All the packages in your layer must  be Linux compatible, since  Lambda functions run on Amazon Linux.

![Lambda Layer Architecture](/images/layer%20architecture.gif)

The diagram above depicts three Lambda functions **A**, **B**, and **C** each function containing its own business logic code.Three shared Lambda layers, `Layer 1`, `Layer 2` and `Layer 3` are mounted at /opt in  function **A** and **B** execution environments whiles  `Layer 1`and `Layer 2` are mounted at /opt in  function `C` execution environment.

Layer 1 contains the common libraries that are used most frequently,such as  `requests` and `boto3` by most AWS applications. Layer 2, packages some  custom utilities such as **authentication** and **logging** functionalities. Layer 3  bundles some ML models, that is only used by Functions **A** and **B** but function **C** doesn't use this layer.


### Layer Versions 
Lambda layers are versioned. A layer version is an immutable snapshot of a layer's specific release. When you add a new layer, Lambda creates a new layer version with the version number 1. When you publish an update to a layer, Lambda automatically increments the version number by 1 and creates a new layer version. Each layer version has a unique Amazon Resource Name (ARN). When adding a layer to a function, ensure you specify the layer version you wish to use.

### Benefits of Using Lambda Layers

- **1.Reduced the size of a function's deployment packages:**Instead of including all of your function dependencies in your deployment package, place them in a layer.  This keeps deployment bundles simple and manageable.
- **2.Separation of Concerns:**Layers can help  separate your function's  business logic from its  dependencies and allows different team members to focus on different aspects of the application.
- **3.Code Reusability**Layers allow you to share dependencies across multiple lambda functions. Without layers, you need to include the same dependencies in each of your function's deployment package which goes agains the the DRY (Don't Repeat Yourself) principle in programming.
- **4.To use the Lambda console code editor:**The code editor is a helpful tool for rapidly evaluating small changes to function code.  However, if your deployment package is too big, you won't be able to use the editor.  Layers allow you to use the code editor and reduce the size of your package.
- **5.Faster Deployment Times:**When you use smaller Lambda deployment packages, your Lambda uploads are faster, resulting in faster function updates.  This efficiency is especially useful in CI/CD pipelines, where deployment speed influences overall development velocity.


### Common Use Cases for AWS Lambda Layers

- **1.Database Connectors:**Database drivers and connectors in applications  often include some complex dependencies, bundling  such dependencies  in a layer ensures that your  database access patterns are uniform for all your Lambda functions.
- **2.Monitoring and Logging Utilities:**You may have some  instrumentation code used for monitoring, logging, and tracing in your applications, it is best practice to use  a shared layer that  can easily be  used across functions without any changes. This makes sure that your applications  uses the same observability best practices.
- **3.Internal Company Libraries:**Many organisations mostly develop their own internal tools and libraries. Packing these tools and libraries as Layers encourages reuse and standardisation in  multiple  projects in the organization.
- **4.Frameworks and SDKs:**Layers can be used  to package complete frameworks or SDKs, ensuring that there is some  consistency in functions.  This approach is good for organization-specific frameworks or some huge third-party SDKs that might otherwise bloat your function packages.

#### Real-World Example of using layers

**Shared Authentication Layer**
Authentication is a common action that is often implemented in many applications  and frequently needed by   multiple lambda functions. A shared authentication  layer that standardize the authentication process is commonly used  for this  functionality. An example of such functionality is demostrated in the code below.

```python
# In the Lambda Layer (python/lib/python3.9/site-packages/auth_utils.py)
import jwt
import os

def verify_token(token):
    """Verify JWT token and return payload if valid"""
    try:
        secret = os.environ['JWT_SECRET']
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return {'valid': True, 'payload': payload}
    except jwt.InvalidTokenError:
        return {'valid': False, 'error': 'Invalid token'}
    except Exception as e:
        return {'valid': False, 'error': str(e)}
```

Multiple functions that need authentication can then use this shared athentication layer as in the below code:

```python
# In the Lambda function
import json
from auth_utils import verify_token

def handler(event, context):
    # Extract token from event
    auth_header = event.get('headers', {}).get('Authorization', '')
    token = auth_header.replace('Bearer ', '') if auth_header else ''
    
    # Verify token
    result = verify_token(token)
    
    if not result['valid']:
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Unauthorized'})
        }
    
    # Continue with authorized operation
    user_id = result['payload']['sub']
    # ...
```





## Creating Your First Lambda Layer

In this section i will walk you through  the process of creating and using  Lambda Layers. In this demo i will be creating a python application that generates a short url given a long url. The main dependencies, will be bundled in a lambda layer.

First we will create a python virtual environments at install all the neccessory dependencies

### Prepare and package your  Lambda layer Content 
**Step 1** Creat a Python virtual environment 
```bash
  python -m venv venv
```
**Step 2** Activate the virtual environment and install the dependcies in the requiremnets.txt file
```bash
  source venv/Scripts/activate
  pip install -r requirements.txt
```
**Step 3** Create a directory called `python`
```bash
  mkdir python 
```
> **Important**: The directory structure matters! Python packages must be in a directory named `python` to be automatically added to the PYTHONPATH when the layer is attached to a Lambda function.
**Step 4** copy the content in venv/Lib/site-packages/ directory  to python/
```bash
   cp -r venv/Lib/site-packages/* python/
```
**Step 4** Zip the content of the python directory
```bash
  zip -r python.zip python
```
### Create and Publish your Lambda Layer in AWS
#### Method 1:Using AWS Console
1. Login into your AWS account and  open the AWS Lambda console
2. Navigate to `Layers`in the left navigation
3. Choose `Create layer`
4. Enter details:
   - **Name**: Give your layer a descriptive name (e.g., `url-shortener-lib`)
   - **Description(Optional)**: enter a description of what's in the layer
   - **Upload ZIP**: Upload your layer zip,`python-layer.zip` file. You can upload directly from you computer or Amazon S3
   - **Compatible architectures(Optional)**: Select  one value or both values. 
   - **Compatible runtimes(Optional)**: Select the appropriate runtimes (e.g., python 3.10 python 3.11 python 3.12, etc.)
   - **License(Optional)**: enter any necessary license information
5. Choose `Create` to publish your layer

  

#### Method 2:Using AWS CLI
  ```bash
  aws lambda publish-layer-version \
    --layer-name url-shortener-lib \
    --description "Layer contains all the dependecies for the url-shortener lambda function" \
    --zip-file fileb://python-layer.zip \
    --compatible-runtimes python3.10 python3.11 python3.12
  ```
> **Important**: If the size of your python.zip file is greater than 10mb, it is recommended to uplaod the zip file to an S3 bucket and use the object ARN.


### Create a Lambda Function 
#### Method 1:Using AWS Console
1. Open the AWS Lambda console
2. Click the "Create function" button
3. Choose one of the creation options:
     - **Author from scratch:** Start with a basic function ✅
     - **Use a blueprint:** Use pre-built templates
     - **Container image:**Deploy from a container image
     - **Browse serverless app repository:** Use existing applications
4 Choose Author from scratch:
    -  **Function name:** Enter a descriptive name (url-shortener)
    -  **Runtime:** Select your preferred runtime (Python 3.12)
    - **Architecture:** Choose x86_64 or arm64
    - **Permissions:** Choose `Create a new role with basic Lambda permissions` 
5. Click "Create function"
6. Upload the code from the python script, `url-shortener.py`.

#### Method 2: Using AWS CLI

```bash
  # Create a basic Lambda function
aws lambda create-function \
    --function-name url-shortener \
    --runtime python3.12 \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --description "My url-shortener function"
```



### Use the Layer in Your Lambda Function (url-shortener)
Now you can attach this layer to any Lambda function:
#### Method 1:Using AWS Console
1. Navigate to your Lambda function ,url-shortener
2. Go to the "Layers" section below the code editor
3. Click "Add a layer"
4. Select "Custom layers"
5. Choose your layer and version
6. Click "Add"

#### Method 2:Using AWS CLI
```bash
aws lambda update-function-configuration \
  --function-name url-shortener \
  --layers arn:aws:lambda:<REGION>:<ACCOUNT-ID>:<lLAMBDA LAYER NAME>:<VERSION>
```
Replace `<REGION>` and `<ACCOUNT-ID>` `<lLAMBDA LAYER NAME>` and `<VERSION>` with the respective values

### Testing  Your Lambda Function.
After you have successfully created your function and layer ,we need to test to make sure everything is working fine. 
1. Click on the "Test" tab (located near the top, next to "Code" and "Configuration")
2. If this is your first test, you'll see "Configure test event" 
3. Click `Create new event`
4. Give your test event a name (url_url-shortener)
```bash
{
  "url": "https://www.example.com/very/long/path/to/some/resource?param1=value1&param2=value2"
}
```
5. Click test.

expected response

```bash
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"original_url\": \"https://www.example.com/very/long/path/to/some/resource?param1=value1&param2=value2\", \"short_url\": \"https://tinyurl.com/abc123\"}"
}
```

## Advanced Layer Techniques

### Multi-language Layers

A single Layer can support multiple runtimes by including the appropriate directory structure for each. For example:

```bash
layer-content/
├── python/
│   └── lib/
│       └── python3.9/
│           └── site-packages/
│               └── shared_package/
└── nodejs/
    └── node_modules/
        └── shared-package/
```

This approach is particularly useful for cross-language utilities or when implementing polyglot applications.

### Layer Size Optimization

Your lambda layers, just like function deployment packages, have a size limit of 250 MB unzipped file. In order to optimize your layer size:
1. Only include  production dependencies in your layer; make sure to  exclude any  development and testing dependencies that will bloat your layer size
2. Use specific and selective imports for large libraries, for example, do not import a whole library but rather import specific components that you need.
3. Try and compress static assets when possible
4. Remove some  unnecessary files like documentation and examples, which are likely to increase the size of your layer
5. Always consider splitting very large dependencies  into multiple Layers 

### Automating Layer Updates
When you have  dependencies that require frequent updates, it is best you consider automating  these  layer updates:
1. You can  first create a CI/CD pipeline that will:
   - periodically checks for dependency updates
   - builds a new Layer version when updates are available
   - publishe the new Layer version
   - and optionally updates functions that depend on the layer to use the new version
2. You can also  use AWS EventBridge to trigger the pipeline on a schedule or in response to security breaches
3. Add  testing and validation of  new Layer versions before deployment.

## Best Practices for using Lambda Layers
The following section describes the best practices that will help you get the most out of Lambda Layers.It is not everything belongs in a Layer. You should consider these guidelines as best practices   when you want to opt for layers:

1. You only use layers when you want to share dependencies  across multiple functions
2. You have large libraries that would bloat your lambda function packages
3. You want to use custom runtimes and some Organization-wide utilities
4. Separating your function business logic from dependencies.
5. Consider versioning  your lambda layers for  layer stability
6. Ensure you regularly scan Layer dependencies for vulnerabilities, and also make sure to audit third-party packages before including them in your  Layers
7. As much as possible, avoid including sensitive data or any  credentials in Layers
8. Monitor and debug functions that use layers.
## Conclusion
AWS Lambda Layers represent  are a great tool that  lets you keep your function deployment packages small and organized by separating your function business logic code from its dependencies. This article dived deep into what lambda layers are, how to create and use layers and some advance concepts and best practices. 
## References and Additional Resources

- [AWS Lambda Layers Documentation](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html)
- [AWS Serverless Application Model (SAM) Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli.html)
- [AWS Lambda Power Tools](https://awslabs.github.io/aws-lambda-powertools-python/)
- [Serverless Framework Documentation](https://www.serverless.com/framework/docs/providers/aws/guide/layers)
- [AWS Lambda Extensions API](https://docs.aws.amazon.com/lambda/latest/dg/runtimes-extensions-api.html)
- [Best practices for working with AWS Lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

---

_This blog post was last updated on May 21, 2025, and reflects the current Lambda Layers functionality as of that date._