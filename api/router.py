from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Annotated, Optional

import bs4
from bs4 import BeautifulSoup

from fastapi import APIRouter, Form, Query, HTTPException, status

from pydantic import HttpUrl

from api.utils import get_full_path, get_request_content
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
    content = get_request_content(url)
    if not content:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Не можемо взяти дані з цього посилання')
    soup = BeautifulSoup(content, 'html.parser')

    title_tag = soup.title   # отримуємо заголовок сайта
    meta_desc = soup.find('meta', {'name': 'description'})  # Намагаємося отримати опис сайту, якщо він є

    description = 'Не знайдено'
    if meta_desc:
        description = meta_desc.attrs['content']

    title = 'У цього сайта немає зоголовку'
    if title_tag:
        title = title_tag.getText()

    return GeneralInfo(title=title, description=description)


@router.post('/get_meta_info/')
async def get_info_site(url: Annotated[HttpUrl, Form()]) -> List[Dict]:
    """Отримати усю мета інформацію на сайті

    Параметри:
        url: посилання на сайт, на якій будемо відправялти запит
    ."""
    content = get_request_content(url)
    if not content:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Не можемо взяти дані з цього посилання')
    soup = BeautifulSoup(content, 'html.parser')

    meta_tags = soup.find_all('meta')   # Отримуємо усі мета теги
    meta = [tag.attrs for tag in meta_tags]    # Як відповідь на запит передаємо атрибути мета тегів

    return meta


@router.post('/get_all_images/')
async def get_all_images(url: Annotated[HttpUrl, Form()]) -> List[Image]:
    """Отримати всі забраження на сайті.

    Параметри:
        url: посилання на сайт, на якій будемо відправялти запит
    """
    content = get_request_content(url)
    if not content:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Не можемо взяти дані з цього посилання')
    soup = BeautifulSoup(content, 'html.parser')

    images = soup.find_all('img')   # Отримуємо усі зображення на сайті
    urls = []

    for image in images:
        image_url = image.attrs.get('src')  # Якщо зображення немає посилання, то пропускаємо
        if not image_url:
            continue

        link = get_full_path(url, image_url)
        urls.append(Image(link=link, description=image.attrs.get('alt')))

    return urls


@router.post('/get_styles_info/')
async def get_styles_info(url: Annotated[HttpUrl, Form()]) -> List[Style]:
    """Отримуємо усі статичні стили сайта

    Параметри:
        url: посилання на сайт, на якій будемо відправялти запит
    """
    content = get_request_content(url)
    if not content:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Не можемо взяти дані з цього посилання')
    soup = BeautifulSoup(content, 'html.parser').head

    styles_tags = soup.find_all('styles')   # Отримуємо усі styles теги
    styles_links = soup.find_all('link', {'rel': 'stylesheet'})   # Усі посилання на стилі
    all_styles = []

    # Перебираємо styles теги
    for tag in styles_tags:
        all_styles.append({'content': tag.getText()})

    # Перебаємо усі посилання на стилі
    for link in styles_links:
        link_url = get_full_path(url, link.attrs.get('href'))
        link_content = get_request_content(link_url)
        if link_content is None:
            continue
        all_styles.append(Style(link=link_url, content=link_content))

    return all_styles


@router.post('/get_scripts_info/')
async def get_scripts_info(url: Annotated[HttpUrl, Form()]) -> List[Script]:
    """Отримуємо усі скрипти сайта

    Параметри:
        url: посилання на сайт, на якій будемо відправялти запит
    """
    content = get_request_content(url)
    if not content:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Не можемо взяти дані з цього посилання')
    soup = BeautifulSoup(content, 'html.parser')

    scripts_tags = soup.findAll('script')   # Отримуємо усі скрипти на сайті
    all_scripts = []

    def get_tag_content(tag: bs4.Tag):
        src = tag.attrs.get('src')
        if src:
            script_url = get_full_path(url, src)
            script_content = get_request_content(script_url)
            if script_content:
                all_scripts.append(Script(link=script_url, content=script_content))
        else:
            all_scripts.append(Script(content=tag.getText()))

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(get_tag_content, scripts_tags)

    return all_scripts


@router.post('/get_quantity_tags/')
async def get_quantity_tags(
        url: Annotated[HttpUrl, Form()],
        tags: Optional[List[str]] = Query(None)
) -> List[Dict]:
    """Отримуємо кількість статичних тегів на сайті

    Параметри:
        url: посилання на сайт, на якій будемо відправялти запит
        tags: перелік тегів, по яким будемо здійснювати перелік
    """
    content = get_request_content(url)
    if not content:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Не можемо взяти дані з цього посилання')
    soup = BeautifulSoup(content, 'html.parser')

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
        counts_tags.append({
            'name': tag,
            'quantity': quantity
        })

    return counts_tags
