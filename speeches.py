#!/usr/bin/env python
from datetime import datetime
from functools import lru_cache
import requests
import click
import csv

BABEL_URL = 'https://babel.labhackercd.leg.br/api/v1/manifestations'


def get_data(url=None, **kwargs):
    click.echo('.', nl=False)
    if url is None:
        response = requests.get(BABEL_URL, params=kwargs)
    else:
        response = requests.get(url)
    response_data = response.json()

    return_data = response_data['results']
    if response_data['next']:
        return_data += get_data(response_data['next'])

    return return_data


def filter_by_stage(stage, data):
    filtered = []
    for speech in data:
        for attribute in speech['attrs']:
            if attribute['field'] == 'fase' and attribute['value'] == stage:
                filtered.append(speech)
                break
    return filtered


@lru_cache()
def get_profile_author_data(url):
    response = requests.get(url)
    return response.json()


def format_data(speech_data):
    meta = {}

    meta['id'] = speech_data['id_in_channel']

    author = get_profile_author_data(speech_data['profile'])
    meta['author_name'] = author['id_in_channel']

    for attr in author['attrs']:
        if attr['field'] == 'partido':
            meta['author_party'] = attr['value']

        if attr['field'] == 'UF':
            meta['author_region'] = attr['value']

    for attr in speech_data['attrs']:
        if attr['field'] == 'dtDiscurso':
            meta['date'] = attr['value']

        if attr['field'] == 'dtAtualizacao':
            meta['updated_at'] = attr['value']

        if attr['field'] == 'fase':
            meta['stage'] = attr['value']

        if attr['field'] == 'original':
            meta['speech'] = attr['value']

    return meta


def write_csv(speeches):
    csv_file = open('speeches.csv', mode='w')
    fieldnames = ['speech', 'id', 'author_name', 'author_party',
                  'author_region', 'date', 'updated_at', 'stage']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for speech in speeches:
        writer.writerow(speech)
    csv_file.close()


@click.command()
@click.argument('initial_date')
@click.argument('end_date')
@click.option('--stage', '-s', help='Initials from speech stage. For example, PE to \'Pequeno Expediente\'')
def main(initial_date, end_date, stage):
    datetime.strptime(initial_date, '%Y-%m-%d')
    datetime.strptime(end_date, '%Y-%m-%d')

    click.echo('Fetching speeches from {} to {}'.format(initial_date, end_date))

    data = get_data(
        manifestation_type__id=1,
        timestamp__gte=initial_date,
        timestamp__lte=end_date,
    )
    if stage:
        click.echo('\nFiltering only {} speeches'.format(stage))
        data = filter_by_stage(stage, data)

    speeches = []
    with click.progressbar(data, label='Formatting data') as bar:
        speeches = [format_data(speech) for speech in bar]

    click.echo('Writing csv')
    write_csv(speeches)


if __name__ == '__main__':
    main()
