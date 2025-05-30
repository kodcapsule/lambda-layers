
import json
import pyshorteners
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda function that generates a short URL from a provided long URL.
    
    Args:
        event (dict): Lambda event containing the original URL
            Expected format: {'url': 'https://example.com/very/long/url'}
            Can also accept API Gateway event with URL in body or queryStringParameters
        context (object): Lambda context object
    
    Returns:
        dict: Response containing the shortened URL and status code
    """
    try:
        # Extract the original URL from the event
        if 'url' in event:
            original_url = event['url']
        elif 'body' in event:
            # Handle API Gateway event with body (POST request)
            body = event['body']
            if isinstance(body, str):
                body = json.loads(body)
            original_url = body.get('url')
        elif 'queryStringParameters' in event and event['queryStringParameters']:
            # Handle API Gateway event with query parameters (GET request)
            original_url = event['queryStringParameters'].get('url')
        else:
            logger.error("No URL provided in the event")
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'No URL provided'})
            }
        
        # Validate the URL
        if not original_url or not original_url.startswith(('http://', 'https://')):
            logger.error(f"Invalid URL format: {original_url}")
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Invalid URL format. URL must start with http:// or https://'})
            }
            
        # Create an instance of the URL shortener service
        shortener = pyshorteners.Shortener()
        
        # Generate the short URL using TinyURL
        short_url = shortener.tinyurl.short(original_url)
        
        logger.info(f"Successfully shortened URL: {original_url} to {short_url}")
        
        # Return the shortened URL in an API Gateway compatible format
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'original_url': original_url,
                'short_url': short_url
            })
        }
    
    except Exception as e:
        logger.error(f"Error generating short URL: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f"Failed to generate short URL: {str(e)}"})
        }