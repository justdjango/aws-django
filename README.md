<p align="center">
  <p align="center">
    <a href="https://justdjango.com/?utm_source=github&utm_medium=logo" target="_blank">
      <img src="https://assets.justdjango.com/static/branding/logo.svg" alt="JustDjango" height="72">
    </a>
  </p>
  <p align="center">
    The Definitive Django Learning Platform.
  </p>
</p>

# Deploying Django on AWS

This guide shows how to deploy Django on AWS using an RDS Postgres DB, Elastic Beanstalk and S3. In order to use this project you will need to add your AWS keys in the .env file.

## Before getting started

You will need to fill in the .env file with your own credentials and create the required resources on your AWS account.

Follow the tutorial series [here](https://www.justdjango.com/courses/deploying-django-using-aws)

## Workflow

When making a change to the project we need to test it before pushing it live. This is the workflow for that:

1. Change into the test branch with `git checkout -b test-branch`
2. Pull the latest version of the master branch with `git pull origin master`
3. Make the change in your code
4. Change the _manage.py_ file to use **awsdjango.settings.test** file (Important)
5. Change the _wsgi.py_ file to use **awsdjango.settings.test** (Important)
6. Change the elasticbeanstalk _config.yml_ file to use the **test** environment (Important)
7. Change the ebextensions _django.config_ file to use **awsdjango.settings.test** (Important)
8. Commit the changes to the test branch
9. Deploy the changes to the AWS test environment with `eb deploy`
10. See if the change works
11. Change the _manage.py_, _wsgi.py_ and _django.config_ files back to use **awsdjango.settings.production** (Important)
12. Change the elasticbeanstalk _config.yml_ file back to use the **production** environment (Important)
13. Commit the changes to the test branch
14. Push the changes to the test branch with `git push origin test`
15. Merge the test branch into the master branch
16. Deploy the now updated project to the AWS production enviroment

## Something important to know about when deploying for the first time to a new environment

In the django.config file are a list of commands to execute after every deployment. For some reason the first deployment fails on the second command. I believe this is because the code needs to be deployed on its own before any commands are included. So to get around this issue, for the first deployment, remove the commands from the config file (commit, push to git) and then deploy. That deployment is just deploying the code. Then add the commands back to the config file (commit, push to git) and deploy again. This time the commands will be executed with no problem because the code is definitely there.

## Development

1. Install dependencies with `pip install -r requirements.txt`
2. Run migrations with `python manage.py migrate`

In this repository, the dev branch is used for working on localhost. To run the server for development use: `python manage.py runserver --settings=awsdjango.settings.development`. The admin user password is `admin`.

**IMPORTANT** - when working in development it's important to use the settings argument: `--settings=awsdjango.settings.development` when necessary to not use the production settings.

## Settings

There are four settings in the projects root folder: **awsdjango**. One for base settings. One for development (localhost), one for testing purposes (live) and one for production (live)

## Configure your AWS environment

Run `aws configure --profile <your_aws_profile_name>` and enter your Access key and secret key which can be created in the IAM section of AWS.

## Deployment with AWS

This project is hosted using Elastic Beanstalk. Elastic Beanstalk is a Platform As A Service (PaaS) that streamlines the setup, deployment, and maintenance of your app on Amazon AWS. It’s a managed service, coupling the server (EC2), database (RDS), and your static files (S3).

The project contains two required EB directories - **.ebextensions** and **.elasticbeanstalk**

The **.ebextensions** contains a config file with settings for the Django project. In the config file the following commands are set to execute on deployment:

1. Make migrations to the database
2. Create a superuser
3. Create required model instances
4. Collect static files

The **.elasticbeanstalk** contains a config file specifying settings. The important ones are the default region of the application, the Python version and environment (production or testing)

From scratch, the deployment process is as follows:

```
pip install awsebcli
eb init
```

Next it will ask for your AWS credentials. You'll need the keys it asks for, which are found in your AWS dashboard.

Now we create an environment:

```
eb create
```

Follow the prompts to create the environment. Afterwards you can use `eb logs` to see the status of the environment. Note when it gives you the **CNAME** of the environment, we need to add that to the projects allowed sources.

Deploy the app with:

```
eb deploy
```

Open the app in the browser with:

```
eb open
```

Now we create an RDS instance. Navigate to your EB instance and click on the environment that was now created. Click on `configuration` in the side panel. Scroll to the bottom and click `Create a new RDS database`. On the RDS setup page change the DB Engine to postgres and add a username and password (note you won't need to specify these in the app as they are environment variables so Django will read them for you). By default the db name is `postgres`.

If you need to configure something on the server, you can ssh into it with `eb ssh`. When setting up the instance you were probably asked if you'd like to create an ssh key pair. You only need to remember the passphrase for the keypair you created. When using ssh you will be asked to enter the passphrase.

## Domain management

DNS records were changed from the domain account manager to AWS and can be managed in the Route53 console. This also means the email host provider (Domain.com in this case) has to have an MX Record linked to its DNS so that mails sent to the AWS name servers are rerouted to the email host.

## SSL

[This Namecheap article](https://www.namecheap.com/support/knowledgebase/article.aspx/467/67/how-to-generate-csr-certificate-signing-request-code) provides a very clear article on creating a CSR needed for accessing your SSL. In this case, because I work on MacOS I used the [Apache OpenSSL/ModSSL/Nginx/Heroku](https://www.namecheap.com/support/knowledgebase/article.aspx/9446/14/generating-csr-on-apache--opensslmodsslnginx--heroku) link.

Place the generated SSL files inside the project root directory. In a terminal run the following command to upload the SSL certificate to AWS:

```
aws iam upload-server-certificate --server-certificate-name awsdjangoCertificate --certificate-body file://awsdjango_com.crt --certificate-chain file://awsdjango_com.ca-bundle --private-key file://server.key
```

Now we need to terminate our load balancer from Http to Https within the configuration settings of our elastic beanstalk environment. Click to _modify_ the Load Balancer and then add a new listener on port 443 with Https that uses our created Certificate. Make sure in the command line you are using the right environment otherwise the certificate will not show up. Use `eb use src-prod --region=<your_region>` to change to the right environment.

## S3

When in production it's good to make use of S3 for hosting static files. This is good for permissions and access to those files, preventing anyone from scraping your css, js and images.

```
<CORSConfiguration>
  <CORSRule>
    <AllowedOrigin>http://www.domain.com</AllowedOrigin>
    <AllowedOrigin>http://domain.com</AllowedOrigin>
    <AllowedOrigin>https://www.domain.com</AllowedOrigin>
    <AllowedOrigin>https://domain.com</AllowedOrigin>
    <AllowedMethod>GET</AllowedMethod>
    <AllowedMethod>HEAD</AllowedMethod>
    <AllowedMethod>DELETE</AllowedMethod>
    <AllowedMethod>PUT</AllowedMethod>
    <AllowedMethod>POST</AllowedMethod>
  </CORSRule>
</CORSConfiguration>
```

Also we most likely need a bucket policy to further specify permissions. Make sure to set all ACL's to False and add the following as a policy:

```
{
    "Version": "2012-10-17",
    "Id": "http referer policy",
    "Statement": [
        {
            "Sid": "Allow get requests originating from www.domain.com and domain.com.",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/*",
            "Condition": {
                "StringLike": {
                    "aws:Referer": [
                        "http://www.domain.com/*",
                        "http://domain.com/*",
                        "https://www.domain.com/*",
                        "https://domain.com/*"
                    ]
                }
            }
        }
    ]
}
```

If more explicit deny settings are needed, add this block into the statement:

```
{
    "Sid": "Explicit deny to ensure requests are allowed only from specific referer.",
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::your-bucket-name/*",
    "Condition": {
        "StringNotLike": {
            "aws:Referer": [
                "http://www.domain.com/*",
                "http://domain.com/*",
                "https://www.domain.com/*",
                "https://domain.com/*"
            ]
        }
    }
}
```

Now everything should be configured for your app so head over to the website and see if its working

---

<div align="center">

<i>Other places you can find us:</i><br>

<a href="https://www.youtube.com/channel/UCRM1gWNTDx0SHIqUJygD-kQ" target="_blank"><img src="https://img.shields.io/badge/YouTube-%23E4405F.svg?&style=flat-square&logo=youtube&logoColor=white" alt="YouTube"></a>
<a href="https://www.twitter.com/justdjangocode" target="_blank"><img src="https://img.shields.io/badge/Twitter-%231877F2.svg?&style=flat-square&logo=twitter&logoColor=white" alt="Twitter"></a>

</div>
