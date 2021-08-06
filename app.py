#!/usr/bin/env python3
from aws_cdk import aws_apigateway, aws_lambda, aws_lambda_python, core


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

        integration = aws_apigateway.LambdaIntegration(
            bopm_lambda,
            proxy=False,
            integration_responses=[
                aws_apigateway.IntegrationResponse(
                    status_code='200',
                    response_parameters={'method.response.header.Access-Control-Allow-Origin': "'*'"}
                )
            ]
        )

        api = aws_apigateway.RestApi(self, id='BopmApiGateway')

        bopm = api.root.add_resource(
            path_part='bopm',
            default_cors_preflight_options=aws_apigateway.CorsOptions(
                allow_origins=aws_apigateway.Cors.ALL_ORIGINS,
                allow_methods=['OPTIONS', 'POST']
            )
        )

        bopm.add_method(
            http_method='POST',
            integration=integration,
            method_responses=[
                aws_apigateway.MethodResponse(
                    status_code='200',
                    response_parameters={'method.response.header.Access-Control-Allow-Origin': True}
                )
            ]
        )


app = core.App()
BopmCdkStack(app, 'BopmCdkStack')
app.synth()
