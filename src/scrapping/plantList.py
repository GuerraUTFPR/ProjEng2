from BeautifulSoup import BeautifulSoup
import requests
import csv
import os

urlSearchTemplate = "http://www.theplantlist.org/tpl1.1/search?q={}"

def getOneEntry(searchTerm):
    response = requests.get(urlSearchTemplate.format(searchTerm))
    raw_http = response.text

    if response.ok:
        raw_http = response.text
        soup = BeautifulSoup(raw_http)

        isAccepted = verifyAccepted(soup)    
        synonymous = getSynonymous(soup)

        return isAccepted, synonymous
    else:
        return 'Bad Response!'

def getAllEntries(inputPath='../data/ListaMacrofitasResult.csv', outputPath='../data/plantList.csv', notFoundPath = '../data/notFoundPlantList.csv'):
    outputFile = open(outputPath, 'a')
    output = csv.writer(outputFile)
    allResponses = []
    with open(inputPath) as input:
        lines = input.readlines()

        for line in lines:
            line = line.replace('\n', '')
            link = urlSearchTemplate.format(line).replace(' ', "%20")
            print link
            response = requests.get(urlSearchTemplate.format(link))

            if response.ok:
                link = link.replace("\n", "")          
                os.system('wget -q -O aux.txt "' + link +  '"')
                web_page = open('aux.txt', 'r')
                raw_http = web_page.read()

                soup = BeautifulSoup(str(raw_http))
                web_page.close()

                title = str(soup('title')[0])

                if "No results" in title:
                    with open(notFoundPath, 'a') as notFound:
                        notFound.write(line + ' not found.')
                    pass
                elif "Search results" in title:                    
                    identifier,genus,species = getCorrectLink(soup)
                    file = open('toProcess.txt', 'a')
                    file.write(identifier + ',' + genus + ' ' + species + '\n')

                else:    
                    result = verifyStatus(soup)      
                    if result == False:
                        status = "SINONIMO"
                        synonymous = getSynonymous(soup)
                        response = line + ',' + status + ',' + synonymous
                        response = response.replace('\n', '')

                    else:
                        status = "NOME_ACEITO"
                        response = line + ',' + status + ',' + line
                        response = response.replace('\n', '')
                    outputFile.write(response + '\n')
    outputFile.close()
    file.close()



def getCorrectLink(soup):
    newName = ""
    table = soup('table')
    trs = table[0]('tr')
    identifier = 'none'
    for tr in trs[1:]:
        genus = str(tr('td')[0]('span')[0]('i')[0].text.encode('utf-8'))
        species = str(tr('td')[0]('span')[0]('i')[1].text.encode('utf-8'))
        status = str(tr('td')[1].text.encode('utf-8'))        

        if status == "Accepted":
            identifier = tr.find('a', href = True)
            identifier = identifier['href']
            break
        else:
            indetifier = 'none'

    return identifier,genus,species

def verifyStatus(soup):
    tag_h1 =  soup('h1')[1]('span')[3]('a')[0]
    status = tag_h1['href']
    print status
    return True if 'accepted' in tag_h1.text else False


def getSynonymous(soup):
    genus = soup('h1')[1]('span')[3]('i')[0].text
    species = soup('h1')[1]('span')[3]('i')[1].text
    return str(genus) + ' ' + str(species)

















def verifyAccepted(soup):
    title = str(soup('title')[0])
    if("No results" in title):
        return False

    try:
        firstTableRow = soup('tbody')[0]
        firstRow = firstTableRow('tr')[0]
        #print firstRow.text
        #print '--------------------------------------------------'
        return True if 'Accepted' in firstRow.text else False
    except Exception as e:
        return False

def getSynonymous_unless(soup):
    title = str(soup('title')[0])

    if("No results" in title):
        return False

    table = soup('table')
    trs = table[0]('tr')
    synonymous = []
    for tr in trs[1:]:
        data = {
            'genus' : str(tr('td')[0]('span')[0]('i')[0].text.encode('utf-8')),
            'species' : str(tr('td')[0]('span')[0]('i')[1].text.encode('utf-8')),
            'status' : str(tr('td')[1].text.encode('utf-8')),
        }
        synonymous.append(data)
    return synonymous

def main():
    getAllEntries()

if __name__ == '__main__':
    main()