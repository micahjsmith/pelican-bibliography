"""
See also:
- http://tug.ctan.org/info/bibtex/tamethebeast/ttb_en.pdf
- https://mirror.kumi.systems/ctan/biblio/bibtex/base/btxdoc.pdf
- http://maverick.inria.fr/~Xavier.Decoret/resources/xdkbibtex/bibtex_summary.html
- https://web.archive.org/web/20190317074837/http://www.lsv.fr:80/~markey/bibla.php
"""
from .lexer import lexer
from .parser import parser
from .models import BibtexEntry

__all__ = ('BibtexEntry', 'lexer', 'parser')
