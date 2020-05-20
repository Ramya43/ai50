import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    numberOfDecimals = 4
    result = {}
    currentPage = corpus[page]
    totalNumberOfPages = len(corpus)

    if len(currentPage) == 0:
        equalProbability = round(1 / len(corpus), numberOfDecimals)
        for x in corpus:
            result[x] = equalProbability

        return result
    
    randomProbability = round(1 - damping_factor, numberOfDecimals)
    randomProbabilityPerPage = round(randomProbability / totalNumberOfPages, numberOfDecimals)
    probabilityPerPage = round(damping_factor / len(currentPage), numberOfDecimals)

    for x in corpus.keys():
        result[x] = randomProbabilityPerPage   

    for x in currentPage:
        result[x] = round(probabilityPerPage + randomProbabilityPerPage, numberOfDecimals)
    
    return result


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    result = {}
    for page in corpus.keys():
        result[page] = 0

    for i in range(n):
        if i == 0:
            page = random.choice(list(corpus.keys()))

        model = transition_model(corpus, page, damping_factor)
        for key in model.keys():
            result[key] = result[key] + model[key]

        population = list(model.keys())
        weights = list(model.values())
        page = random.choices(population, weights=weights)[0]

    for key in result.keys():
        result[key] = round(result[key] / n, 4)
        
    return result
        


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
