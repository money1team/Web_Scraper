def extract_headings(soup):
    headings = {}
    for level in range(1, 7):
        headings[f'h{level}'] = [h.get_text(strip=True) for h in soup.find_all(f'h{level}')]
    return headings

def extract_paragraphs(soup):
    return [p.get_text(strip=True) for p in soup.find_all('p')]

def extract_links(soup):
    return {a.get_text(strip=True): a['href'] for a in soup.find_all('a', href=True)}
