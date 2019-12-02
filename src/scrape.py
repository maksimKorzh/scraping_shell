# Import libraries
import requests
from bs4 import BeautifulSoup
from tabulate import *
from cmd import *
import sys
import re
import json



class Scraper(Cmd):
    intro = 'Scraping shell v 0.0.1 by Code Monkey King\nType "help" to get the list of commands'
    prompt = '\nscrape > '
    
    response = None
    content = None
    ignored_tags = ['script', 'style']

    def do_fetch(self, url):
        '''Makes HTTP GET request to the given URL'''
        if url == '':
            print(' Please provide a URL!')
            return
        try:
            print(' Making HTTP GET request to URL: %s' % url)
            response = requests.get(url)

            if response.status_code == 200:
                print(' Status code: %s' % response.status_code)
                self.response = response
                self.content = BeautifulSoup(response.text, 'lxml')
            else:
                print('\n Failure | Status code: %s' % response.status_code)

        except:
            print('\n Failed to fetch URL: %s' % url)

    
    def do_html(self, no_arg):
        if self.content is not None:
            print(self.content.prettify())
        else:
            print(' Content is not loaded, please fetch URL first!')
    
    def do_text(self, no_arg):
        if self.content is not None:
            for tag in self.content.recursiveChildGenerator():
                if tag.name is None and not tag.isspace() and tag.parent.name not in self.ignored_tags and tag != 'html':
                    indent = ''
                    
                    for space in range(0, len([tag for tag in tag.parents])):
                        indent += ' '
                    
                    if tag.parent.name == 'a':
                        print(indent + '[' + tag.strip() + ']' + ' <' + tag.parent['href'] + '>')
                    else:
                        print(indent + tag.strip())
        else:
            print(' Content is not loaded, please fetch URL or load stored HTML first!')

    def do_search(self, text):
        if self.content is not None:
            results = self.content.findAll(text=re.compile(text))
            print()
            
            for result in results:
                print(json.dumps({
                    'name': result.parent.name,
                    'text': result,
                    'attributes': result.parent.attrs
                }, indent=2), '\n')
        else:
            print(' Content is not loaded, please fetch URL or load stored HTML first!')

    def do_extract(self, query):
        if self.content is not None:
            tag = query.split(',')[0]
            
            try:
                attrs = query.split(',')[1]
                params = json.loads(attrs)
            except:
                params = ''
                
            
            results = self.content.findAll(tag, params)
            
            print()
            if tag == 'a':
                try:
                    print('\n'.join(['[' + result.text + ']' + ' <' + result['href'] + '>' for result in results]))
                except:
                    print('\n'.join([result.text for result in results]))
            else:
                print('\n'.join([result.text for result in results]))
            print('\n Total: %d entries' % len(results))
        else:
            print(' Content is not loaded, please fetch URL or load stored HTML first!')

    def do_tables(self, no_arg):
        if self.content is not None:
            results = self.content.findAll('table')
            
            if not len(results):
                print(' No tables available on the page!')
                return
            
            for table in results:
                print('\n table', table.attrs)
                results = []
                rows = table.findAll('tr')
                headers = [header.text for header in table.findAll('th')]
                
                for row in rows:
                    if len(row.findAll('td')):
                        results.append([column.text[:50] for column in row.findAll('td')])

                print(tabulate(results, headers, tablefmt='fancy_grid'))
        else:
            print(' Content is not loaded, please fetch URL or load stored HTML first!')


    def do_save(self, filename):
        if self.response is not None:
            if filename == '':
                filename = 'res.html'

            print(' Writing content to file: "%s" |' % filename, end=' ')

            with open('./html/' + filename, 'w') as html:
                html.write(self.response.text)
            
            print('Done')
        else:
            print(' Content is not loaded, please fetch URL first')

    def do_load(self, filename):
        try:
            if filename == '':
                filename = 'res.html'
            
            print(' Reading content from file: "%s" |' % filename, end=' ')
            
            source = ''
            
            with open('./html/' + filename, 'r') as html:
                for line in html.read():
                    source += line
            
            self.content = BeautifulSoup(source, 'lxml')
            print('Done')

        except FileNotFoundError:
            print(' File "%s" not found!' % filename)

    def do_exit(self, arg):
        print('\n\nThank you for using scraping shell!\n')
        sys.exit()

if __name__ == '__main__':
    scraper = Scraper()
    scraper.cmdloop()
