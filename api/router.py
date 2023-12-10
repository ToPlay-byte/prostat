import re

from typing import List, Dict, Annotated, Optional
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup

from fastapi import APIRouter, Form, Query
from fastapi.responses import Response

from pydantic import HttpUrl

from api.utils import get_full_path
from api.models import (
    GeneralInfo, Image,
    Style, Script
)


router = APIRouter(
    prefix='/api',
    tags=['API documentation']
)


@router.post('/get_general_info/')
async def get_general_info(url: Annotated[HttpUrl, Form()]) -> GeneralInfo:
    """Отрмати заголовок сайта та його опис(якщо він існує).

    Параметри:
        url: посилання на сайт, на якій будемо відправялти запит
    """
    req = requests.get(url)
    print(req.text)
    soup = BeautifulSoup(req.text, 'html.parser')

    title = soup.title.getText()    # отримуємо заголовок сайта
    meta_desc = soup.find('meta', {'name': 'description'})  # Намагаємося отримати опис сайту, якщо він є

    description = 'Не знайдено'
    if meta_desc:
        description = meta_desc.attrs['content']

    return {
        'title': title,
        'description': description
    }


@router.post('/get_meta_info/')
async def get_info_site(url: Annotated[HttpUrl, Form()]) -> List[Dict]:
    """Отримати усю мета інформацію на сайті

    Параметри:
        url: посилання на сайт, на якій будемо відправялти запит
    ."""
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')

    meta_tags = soup.find_all('meta')   # Отримуємо усі мета теги
    meta = [tag.attrs for tag in meta_tags]    # Як відповідь на запит передаємо атрибути мета тегів

    return meta


@router.post('/get_all_images/')
async def get_all_images(url: Annotated[HttpUrl, Form()]) -> List[Image]:
    """Отримати всі забраження на сайті.

    Параметри:
        url: посилання на сайт, на якій будемо відправялти запит
    """
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')

    images = soup.find_all('img')   # Отримуємо усі зображення на сайті
    urls = []

    for image in images:
        image_url = image.attrs.get('src')  # Якщо зображення немає посилання, то пропускаємо
        if not image_url:
            continue

        link = get_full_path(url, image_url)
        urls.append({'link': link, 'description': image.attrs.get('alt')})

    return urls


@router.post('/get_styles_info/')
async def get_styles_info(url: Annotated[HttpUrl, Form()]) -> List[Style]:
    """Отримуємо усі статичні стили сайта

    Параметри:
        url: посилання на сайт, на якій будемо відправялти запит
    """
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser').head

    styles_tags = soup.find_all('styles')   # Отримуємо усі styles теги
    styles_links = soup.find_all('link', {'rel': 'stylesheet'})   # Усі посилання на стилі
    all_styles = []

    # Перебираємо styles теги
    for tag in styles_tags:
        all_styles.append({'content': tag.getText()})

    # Перебаємо усі посилання на стилі
    for link in styles_links:
        link_url = get_full_path(url, link.attrs.get('href'))
        link_content = requests.get(link_url).text
        all_styles.append({'link': link_url, 'content': link_content})

    return all_styles


@router.post('/get_scripts_info/')
async def get_scripts_info(url: Annotated[HttpUrl, Form()]) -> List[Script]:
    """Отримуємо усі статичні стили сайта

    Параметри:
        url: посилання на сайт, на якій будемо відправялти запит
    """
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')

    scripts_tags = soup.findAll('script')   # Отримуємо усі скрипти на сайті
    all_scripts = []

    for tag in scripts_tags:
        if tag.has_attr('src'):
            script_url = tag.attrs.get('src')
            script_content = requests.get(script_url).text
            all_scripts.append({'link': script_url, 'content': script_content})
        else:
            all_scripts.append({'content': tag.getText()})

    return all_scripts


@router.post('/get_quantity_tags/')
async def get_quantity_tags(url: Annotated[HttpUrl, Form()], tags: Optional[List[str]] = Query(None)) -> List[Dict]:
    """Отримуємо кількість статичних тегів на сайті

    Параметри:
        url: посилання на сайт, на якій будемо відправялти запит
        tags: перелік тегів, по яким будемо здійснювати перелік
    """
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')

    counts_tags = []
    if tags is None:
        tags = [
            'a', 'div', 'p',
            'img', 'h1', 'h2',
            'h3', 'h4', 'h5',
            'h6', 'li', 'ul'
        ]

    for tag in tags:
        quantity = len(soup.find_all(tag))
        if quantity:
            counts_tags.append({
                'name': tag,
                'quantity': quantity
            })

    return counts_tags

