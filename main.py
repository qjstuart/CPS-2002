import map
from pyhtml import *


def f_links(ctx):
    for title, page in [('Home', '/home.html'),
                        ('Login', '/login.html')]:
        yield li(a(href=page)(title))


t = html(
    head(
        title('Awesome website'),
        script(src="http://path.to/script.js")
    ),
    body(
        header(
            img(src='/path/to/logo.png'),
            nav(
                ul(f_links)
            )
        ),
        div(
            lambda ctx: "Hello %s" % ctx.get('user', 'Guest'),
            'Content here'
        ),
        footer(
            hr,
            'Copyright 2013'
        )
    )
)

print(t.render(user='user'))
render = t.render()
f = open("map_player_n.html", "w")
f.write(render)