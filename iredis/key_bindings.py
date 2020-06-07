import logging

from prompt_toolkit.filters import completion_is_selected
from prompt_toolkit.key_binding import KeyBindings

logger = logging.getLogger(__name__)

kb = KeyBindings()


@kb.add("enter", filter=completion_is_selected)
def _(event):
    """Makes the enter key work as the tab key only when showing the menu.
    In other words, don't execute query when enter is pressed in
    the completion dropdown menu, instead close the dropdown menu
    (accept current selection).
    """
    logger.debug("Detected enter key.")

    event.current_buffer.complete_state = None
    b = event.app.current_buffer
    b.complete_state = None
