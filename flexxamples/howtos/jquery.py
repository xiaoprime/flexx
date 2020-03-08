# doc-export: Example
"""
Example to demonstrate a jQuery widget.
This demonstrates how Flexx can interact wih other JS frameworks.
"""

from pscript import RawJS

from flexx import flx
from flexx import event

# Associate assets needed by this app.
flx.assets.associate_asset(__name__, "http://code.jquery.com/jquery-1.10.2.js")
flx.assets.associate_asset(__name__, "http://code.jquery.com/ui/1.11.4/jquery-ui.js")
flx.assets.associate_asset(__name__,
    "http://code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css")


class DatePicker(flx.Widget):

    def _create_dom(self):
        global window
        node = window.document.createElement('input')
        RawJS('$')(node).datepicker()
        return node


class AutoComplete(flx.Widget):

    options = event.ListProp(['yes', 'no', 'I have no idea.'], settable=True, doc="""
        """)

    def _create_dom(self):
        global window
        self.node = window.document.createElement('input')
        RawJS('$')(self.node).autocomplete({'source': self.options})
        self._addEventListener(self.node, 'blur', self.user_done, False)
        return self.node

    @event.reaction('options')
    def refresh(self):
        RawJS('$')(self.node).autocomplete({'source': self.options})


    @event.emitter
    def user_done(self):
        """ Event emitted when the user is done editing the text, either by
        moving the focus elsewhere, or by hitting enter.
        Has ``old_value`` and ``new_value`` attributes (which are the same).
        """
        d = {'key': self.node.value}
        return d

class Example(flx.Widget):

    def init(self):

        with flx.FormLayout():
            self.start = DatePicker(title='Start date')
            self.end = DatePicker(title='End date')
            self.auto = AutoComplete(title='')
            flx.Widget(flex=1)


if __name__ == '__main__':
    m = flx.launch(Example, 'app')
    flx.run()
