from parent import LinkedIn
from copy import deepcopy
from constant import SEARCH_HEADERS
from traceback import print_exc
import requests_cache



class Child(LinkedIn):
    search_endpoint = 'https://www.linkedin.com:443/voyager/api/graphql?'


    def search(self, keyword):
        query = f'includeWebMetadata=true&variables=(start:0,origin:SWITCH_SEARCH_VERTICAL,query:(keywords:{keyword},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.0814efb14ee283f3e918ff9608d705fd'
        # query = f'variables=(start:0,origin:GLOBAL_SEARCH_HEADER,query:(keywords:{keyword},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.181547298141ca2c72182b748713641b'
        url = self.search_endpoint + query
        headers = self.build_headers(keyword)
        response = self.request(url, headers=headers, cookies=self.cookies)
        return response.json()


    def parse(self, result):
        if result:
            for element in result.get('included'):
                if element.get('entityUrn'):
                    # got fsd_profile_urn
                    urn = element.get('entityUrn')
                    # determine is connect possible ( monday )
                    

    def build_headers(self, keyword):
        headers = deepcopy(SEARCH_HEADERS)
        # headers['Referer'] = f'https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=GLOBAL_SEARCH_HEADER'
        headers['Csrf-Token'] = self.cookies.get("JSESSIONID").replace('"','')
        return headers


    def crawl(self):
        if not self.load_cookies():
            self.login()
        if self.logged_in:
            print('logged in')
            keyword = 'Amir'
            result = self.search(keyword)
            self.parse(result)




crawler = Child()
crawler.crawl()



# need fsd_profile_urn
"""
import requests

cookies = {
    'bcookie': '"v=2&56bb6c67-f960-44ce-839f-d940dab19140"',
    'bscookie': '"v=1&202303311021305f435b99-cfc8-4ed7-8b63-e2cf5076c470AQElF9PKz9lYBatFgd__7JzLy2aFUZb5"',
    'G_ENABLED_IDPS': 'google',
    'aam_uuid': '21626498121471920013596951334606098972',
    'lang': 'v=2&lang=en-us',
    'AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg': '1',
    'li_at': 'AQEDAUC_ZkcA_QpqAAABhzc3VHUAAAGHW0PYdU4AWJp4SzzJ_aEP8kM7meSDLWFVydwK7rtKOzcwXP0-e-L6Oytarg3HWykwxIGi9J6GoUsxxJBx1qfcUTfye4baW66F9fBW99Id-w-y0StIvCWJPeQa',
    'liap': 'true',
    'JSESSIONID': '"ajax:8127753089859098663"',
    'timezone': 'Asia/Karachi',
    'li_theme': 'light',
    'li_theme_set': 'app',
    'li_sugr': 'cd999f6d-9e7b-4af9-ac8d-ed2f90f6f1b6',
    '_guid': '89545545-c61d-4f18-b909-d14700716d23',
    'UserMatchHistory': 'AQI6-oUIuPO7YwAAAYc3N4GL8r0oTDcsSTXjemitm983hugvNFt_lxV1xfYddyoqUBqGcEbIq65BqSxm7HBq8kAtR6VF3W5VXk8cGDJHdGDsKfxhb7_htAMGZUOzwJVMY42XoP_BmEEST8g_ZA0b6IYNiobuCWahO32q5Qm9e9dfcT0fwtPXLN4UBb-GffIJK8pi5wqXK2N0v6JX14ZqVLWnitJy6UwvvU1OZetZG_g8tqvNOIRr4ock7cVIP2pTaTUHuO5xvZWv7rm13PL-ji3MSQRihqqTln7Kk40',
    'AnalyticsSyncHistory': 'AQKcOrK4d65cugAAAYc3N4GL6ZXxS1NN6U3QQnOxzLxhUXAupdpgKCU7rYNxwOeZrxFT9TpJpYntj5_Sm2LHkg',
    'AMCV_14215E3D5995C57C0A495C55%40AdobeOrg': '-637568504%7CMCIDTS%7C19448%7CMCMID%7C22192649532077309543541481953912070615%7CMCAAMLH-1680863397%7C3%7CMCAAMB-1680863397%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1680265797s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C326679661',
    'lms_ads': 'AQFrBym413tdpgAAAYc3N4L8Q77RO9pCXMdwfxJPT7S5s9UL7oLPDSFAxioW6khgD-tohI4quxwfAdNq3sw8Ig1OXlpZX7NX',
    'lms_analytics': 'AQFrBym413tdpgAAAYc3N4L8Q77RO9pCXMdwfxJPT7S5s9UL7oLPDSFAxioW6khgD-tohI4quxwfAdNq3sw8Ig1OXlpZX7NX',
    'lidc': '"b=VB83:s=V:r=V:a=V:p=V:g=3101:u=2:x=1:i=1680258600:t=1680344986:v=2:sig=AQFSOCv6goASKJemw0nJeMZ8vYfvc_pD"',
}

headers = {
    'Host': 'www.linkedin.com',
    # 'Content-Length': '82',
    'Sec-Ch-Ua': '"Chromium";v="111", "Not(A:Brand";v="8"',
    'X-Li-Lang': 'en_US',
    'Sec-Ch-Ua-Mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.111 Safari/537.36',
    'X-Li-Page-Instance': 'urn:li:page:d_flagship3_search_srp_people;vFDFf4i2SNasE5sxOJ7wrQ==',
    'Content-Type': 'application/json; charset=UTF-8',
    'Accept': 'application/vnd.linkedin.normalized+json+2.1',
    'Csrf-Token': 'ajax:8127753089859098663',
    'X-Li-Track': '{"clientVersion":"1.12.2138","mpVersion":"1.12.2138","osName":"web","timezoneOffset":5,"timezone":"Asia/Karachi","deviceFormFactor":"DESKTOP","mpName":"voyager-web","displayDensity":1,"displayWidth":1680,"displayHeight":1050}',
    'X-Restli-Protocol-Version': '2.0.0',
    'X-Li-Deco-Include-Micro-Schema': 'true',
    'X-Li-Pem-Metadata': 'Voyager - Invitations=send-invite',
    'Sec-Ch-Ua-Platform': '"Linux"',
    'Origin': 'https://www.linkedin.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.linkedin.com/search/results/people/?keywords=asif&origin=SWITCH_SEARCH_VERTICAL&sid=N2%40',
    # 'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    # 'Cookie': 'bcookie="v=2&56bb6c67-f960-44ce-839f-d940dab19140"; bscookie="v=1&202303311021305f435b99-cfc8-4ed7-8b63-e2cf5076c470AQElF9PKz9lYBatFgd__7JzLy2aFUZb5"; G_ENABLED_IDPS=google; aam_uuid=21626498121471920013596951334606098972; lang=v=2&lang=en-us; AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg=1; li_at=AQEDAUC_ZkcA_QpqAAABhzc3VHUAAAGHW0PYdU4AWJp4SzzJ_aEP8kM7meSDLWFVydwK7rtKOzcwXP0-e-L6Oytarg3HWykwxIGi9J6GoUsxxJBx1qfcUTfye4baW66F9fBW99Id-w-y0StIvCWJPeQa; liap=true; JSESSIONID="ajax:8127753089859098663"; timezone=Asia/Karachi; li_theme=light; li_theme_set=app; li_sugr=cd999f6d-9e7b-4af9-ac8d-ed2f90f6f1b6; _guid=89545545-c61d-4f18-b909-d14700716d23; UserMatchHistory=AQI6-oUIuPO7YwAAAYc3N4GL8r0oTDcsSTXjemitm983hugvNFt_lxV1xfYddyoqUBqGcEbIq65BqSxm7HBq8kAtR6VF3W5VXk8cGDJHdGDsKfxhb7_htAMGZUOzwJVMY42XoP_BmEEST8g_ZA0b6IYNiobuCWahO32q5Qm9e9dfcT0fwtPXLN4UBb-GffIJK8pi5wqXK2N0v6JX14ZqVLWnitJy6UwvvU1OZetZG_g8tqvNOIRr4ock7cVIP2pTaTUHuO5xvZWv7rm13PL-ji3MSQRihqqTln7Kk40; AnalyticsSyncHistory=AQKcOrK4d65cugAAAYc3N4GL6ZXxS1NN6U3QQnOxzLxhUXAupdpgKCU7rYNxwOeZrxFT9TpJpYntj5_Sm2LHkg; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C19448%7CMCMID%7C22192649532077309543541481953912070615%7CMCAAMLH-1680863397%7C3%7CMCAAMB-1680863397%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1680265797s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C326679661; lms_ads=AQFrBym413tdpgAAAYc3N4L8Q77RO9pCXMdwfxJPT7S5s9UL7oLPDSFAxioW6khgD-tohI4quxwfAdNq3sw8Ig1OXlpZX7NX; lms_analytics=AQFrBym413tdpgAAAYc3N4L8Q77RO9pCXMdwfxJPT7S5s9UL7oLPDSFAxioW6khgD-tohI4quxwfAdNq3sw8Ig1OXlpZX7NX; lidc="b=VB83:s=V:r=V:a=V:p=V:g=3101:u=2:x=1:i=1680258600:t=1680344986:v=2:sig=AQFSOCv6goASKJemw0nJeMZ8vYfvc_pD"',
}

params = {
    'action': 'verifyQuotaAndCreate',
    'decorationId': 'com.linkedin.voyager.dash.deco.relationships.InvitationCreationResultWithInvitee-2',
}

json_data = {
    'inviteeProfileUrn': 'urn:li:fsd_profile:ACoAABfBQIcBIX_A-IoC-vywpD4X0NGe9MPy2xE',
}

response = requests.post(
    'https://www.linkedin.com/voyager/api/voyagerRelationshipsDashMemberRelationships',
    params=params,
    cookies=cookies,
    headers=headers,
    json=json_data,
    verify=False,
)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"inviteeProfileUrn":"urn:li:fsd_profile:ACoAABfBQIcBIX_A-IoC-vywpD4X0NGe9MPy2xE"}'
#response = requests.post(
#    'https://www.linkedin.com/voyager/api/voyagerRelationshipsDashMemberRelationships',
#    params=params,
#    cookies=cookies,
#    headers=headers,
#    data=data,
#    verify=False,
#)
"""