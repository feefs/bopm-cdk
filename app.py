#!/usr/bin/env python3
from aws_cdk import aws_apigateway, aws_iam, aws_lambda, aws_lambda_python, core


class BopmCdkStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bopm_lambda = aws_lambda_python.PythonFunction(
            self,
            id='lambda',
            function_name='BopmLambda',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            timeout=core.Duration.seconds(60),
            memory_size=512,
            entry='./bopm_cdk/bopm',
            handler='handler',
            index='bopm_lambda.py'
        )

        github_pages_ips = ['185.199.108.153', '185.199.109.153', '185.199.110.153', '185.199.111.153']

        api = aws_apigateway.LambdaRestApi(
            self,
            id='lambda-apigateway',
            handler=bopm_lambda,
            proxy=False,
            policy=aws_iam.PolicyDocument(
                statements=[
                    aws_iam.PolicyStatement(
                        effect=aws_iam.Effect.DENY,
                        principals=[aws_iam.AnyPrincipal()],
                        actions=['execute-api:Invoke'],
                        conditions={'NotIpAddress': {'aws:SourceIp': github_pages_ips}},
                    )
                ]
            )
        )

        bopm = api.root.add_resource('bopm')
        bopm.add_method('PUT')


app = core.App()
BopmCdkStack(app, 'BopmCdkStack')
app.synth()
