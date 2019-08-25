import json
import google_scrapper

g_scrapper = google_scrapper


def lambda_handler(event, context):
    __url = event['queryStringParameters']['url']
    __is_mobile = event['queryStringParameters'].get('m', '0')
    __is_mobile = int(__is_mobile)

    results = g_scrapper.scrape(url=__url, is_mobile=__is_mobile)

    return {
        'statusCode': 200,
        'body': json.dumps({'results': results, 'url': __url, 'is_mobile': __is_mobile})
    }
