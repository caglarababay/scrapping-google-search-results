import json
from google_scrapper import GoogleCrawler

#g_scrapper = google_scrapper


def lambda_handler(event, context):
    __url = event['queryStringParameters']['url']
    __is_mobile = event['queryStringParameters'].get('m', '0')
    __is_mobile = int(__is_mobile)

    google_crawler = GoogleCrawler(__url, __is_mobile)

    results = google_crawler.run()

    return {
        'statusCode': 200,
        'body': json.dumps({'results': results, 'url': __url, 'is_mobile': __is_mobile})
    }
