"""Wikidot syntax parser - converts Wikidot markup to clean HTML/Markdown."""

import re

class WikidotParser:
    """Parses Wikidot syntax into clean HTML and Markdown."""

    @staticmethod
    def parse_wikidot(text: str) -> str:
        """Convert Wikidot syntax to HTML."""
        if not text:
            return ""

        html = text

        # Headers
        html = re.sub(r'^\+{1,5} (.+)$', lambda m: f'<h{len(m.group(0).strip().split(" ")[0])}>{m.group(1)}</h{len(m.group(0).strip().split(" ")[0])}>', html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'//(.+?)//', r'<em>\1</em>', html)

        # Strikethrough
        html = re.sub(r'--(.+?)--', r'<del>\1</del>', html)

        # Underline
        html = re.sub(r'__(.+?)__', r'<u>\1</u>', html)

        # Links [[[page | text]]] or [[[page]]]
        html = re.sub(r'\[\[\[([^\|]+?)(?:\|(.+?))?\]\]\]', r'<a href="/scp/\1">\2</a>', html)

        # External links [[url text]]
        html = re.sub(r'\[\[([^\s]+)\s+(.+?)\]\]', r'<a href="\1" rel="noopener">\2</a>', html)

        # Blockquotes
        html = re.sub(r'^>(.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

        # Horizontal rules
        html = re.sub(r'^----+$', '<hr>', html, flags=re.MULTILINE)

        # Lists (simple)
        html = re.sub(r'^(\s*)\* (.+)$', r'\1<li>\2</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^(\s*)# (.+)$', r'\1<li>\2</li>', html, flags=re.MULTILINE)

        # Collapsible blocks [[collapsible show="..." hide="..."]]
        html = re.sub(
            r'\[\[collapsible[^\]]*\]\](.+?)\[\[/collapsible\]\]',
            r'<details><summary>Show</summary>\1</details>',
            html, flags=re.DOTALL
        )

        # Tables [[table]] ... [[/table]]
        html = re.sub(r'\[\[table\]\]', '<table>', html)
        html = re.sub(r'\[\[/table\]\]', '</table>', html)

        # Remove [[module]] tags
        html = re.sub(r'\[\[module[^\]]*\]\]', '', html)
        html = re.sub(r'\[\[/module\]\]', '', html)

        # Remove [[div]] tags
        html = re.sub(r'\[\[div[^\]]*\]\]', '<div>', html)
        html = re.sub(r'\[\[/div\]\]', '</div>', html)

        # [[span]] tags
        html = re.sub(r'\[\[span[^\]]*\]\]', '<span>', html)
        html = re.sub(r'\[\[/span\]\]', '</span>', html)

        # Code blocks [[code]] ... [[/code]]
        html = re.sub(r'\[\[code\]\]', '<pre><code>', html)
        html = re.sub(r'\[\[/code\]\]', '</code></pre>', html)

        # Images [[image URL]]
        html = re.sub(r'\[\[image\s+([^\]]+)\]\]', r'<img src="\1" alt="Image" />', html)

        # [[include]] tags - remove but note them
        html = re.sub(r'\[\[include\s+[^\]]*\]\]', '', html)

        # Paragraph wrapping for remaining text blocks
        lines = html.split('\n')
        result = []
        in_block = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                in_block = False
                result.append('')
                continue
            if stripped.startswith('<') and not stripped.startswith('<li>'):
                in_block = True
                result.append(line)
                continue
            if in_block:
                result.append(line)
            else:
                result.append(f'<p>{line}</p>')

        html = '\n'.join(result)
        html = re.sub(r'<p>\s*</p>', '', html)

        return html

    @staticmethod
    def strip_wikidot(text: str) -> str:
        """Strip Wikidot syntax and return plain text."""
        if not text:
            return ""

        plain = text
        plain = re.sub(r'\*\*(.+?)\*\*', r'\1', plain)
        plain = re.sub(r'//(.+?)//', r'\1', plain)
        plain = re.sub(r'--(.+?)--', r'\1', plain)
        plain = re.sub(r'__()__', r'\1', plain)
        plain = re.sub(r'\[\[\[([^\|]+?)(?:\|(.+?))?\]\]\]', r'\1', plain)
        plain = re.sub(r'\[\[[^\]]+\]\]', '', plain)
        plain = re.sub(r'\[\[/.*?\]\]', '', plain)
        plain = re.sub(r'^[+*>#]+\s*', '', plain, flags=re.MULTILINE)
        plain = re.sub(r'----+', '', plain)
        return plain.strip()