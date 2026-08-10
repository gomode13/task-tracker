from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)


def render_template(template_name: str, **context) -> str:
    template = env.get_template(template_name)
    return template.render(**context)
