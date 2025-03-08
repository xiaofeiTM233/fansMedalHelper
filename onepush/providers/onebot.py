"""
@Project   : onepush
@Author    : 飞小RAN
@Blog      : https://hitfun.top
"""

from ..core import Provider


class OneBot(Provider):
    name = 'onebot'
    base_url = '{}/{}?access_token={}'
    site_url = 'https://11.onebot.dev/'

    _params = {
        'required': ['key'],
        'optional': ['title', 'content', 'qq']
    }

    async def _prepare_url(self, url: str, key: str, mode: str = 'send_private_msg', **kwargs):
        self.url = self.base_url.format(url, mode, key)
        return self.url

    async def _prepare_data(self,
                      title: str = None,
                      content: str = None,
                      qq: str = None,
                      **kwargs):
        message = self.process_message(title, content)
        self.data = {
            'message': message,
            'user_id': qq
        }
        return self.data

    async def _send_message(self):
        return await self.request('post', self.url, json=self.data)
