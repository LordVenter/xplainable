from traitlets import traitlets
import ipywidgets as widgets
from ipywidgets import interactive
from IPython.display import display

class LiveDF:

    def __init__(self, df):
        self.df = df

    def __call__(self):
        
        def _set_params(visualise=True):
            if visualise:
                display(self.df)

        return interactive(_set_params)


adder_element_layout = widgets.Layout(
    width='260px',
    margin='0 0 10px 0'
)
adder_element_style = {'description_width': 'initial'}

class Dropdown(widgets.Dropdown):
    """This is used to set a default max_width for adder dropdowns"""
    
    def __init__(self, *args, **kwargs):
        super(Dropdown, self).__init__(*args, **kwargs)
        self.layout = adder_element_layout
        self.style = adder_element_style


class Text(widgets.Text):
    """This is used to set a default max_width for adder Text"""
    
    def __init__(self, *args, **kwargs):
        super(Text, self).__init__(*args, **kwargs)
        self.layout = adder_element_layout
        self.style = adder_element_style


class IntText(widgets.IntText):
    """This is used to set a default max_width for adder Text"""
    
    def __init__(self, *args, **kwargs):
        super(IntText, self).__init__(*args, **kwargs)
        self.layout = adder_element_layout
        self.style = adder_element_style


class SelectMultiple(widgets.SelectMultiple):
    """This is used to set a default max_width for adder Text"""
    
    def __init__(self, *args, **kwargs):
        super(SelectMultiple, self).__init__(*args, **kwargs)
        self.layout = adder_element_layout
        self.style = adder_element_style

class TagsInput(widgets.TagsInput):
    """This is used to set a default max_width for adder Text"""
    
    def __init__(self, *args, **kwargs):
        super(TagsInput, self).__init__(*args, **kwargs)
        self.layout = adder_element_layout
        self.style = adder_element_style


class Checkbox(widgets.Checkbox):
    """This is used to set a default max_width for adder Text"""
    
    def __init__(self, *args, **kwargs):
        super(Checkbox, self).__init__(*args, **kwargs)
        self.layout = adder_element_layout
        self.style = adder_element_style


class ToggleButtons(widgets.ToggleButtons):
    """This is used to set a default max_width for adder Text"""
    
    def __init__(self, *args, **kwargs):
        super(ToggleButtons, self).__init__(*args, **kwargs)
        self.layout = adder_element_layout
        self.style = {'description_width': 'initial', "button_width": "auto"}


class IntSlider(widgets.IntSlider):
    """This is used to set a default max_width for adder Text"""
    
    def __init__(self, *args, **kwargs):
        super(IntSlider, self).__init__(*args, **kwargs)
        self.layout = adder_element_layout
        self.style = adder_element_style


class FloatSlider(widgets.FloatSlider):
    """This is used to set a default max_width for adder Text"""
    
    def __init__(self, *args, **kwargs):
        super(FloatSlider, self).__init__(*args, **kwargs)
        self.layout = adder_element_layout
        self.style = adder_element_style


class TrainButton(widgets.Button):
    """ Button that stores model state

    Args:
        model: xplainable model
    """

    def __init__(self, partitions=None, *args, **kwargs):
        super(TrainButton, self).__init__(*args, **kwargs)
        self.add_traits(partitions=traitlets.Any(partitions))


class TransformerButton(widgets.Button):
    """ Button that stores model state

    Args:
        model: xplainable model
    """

    def __init__(self, transformer=None, df=None, *args, **kwargs):
        super(TransformerButton, self).__init__(*args, **kwargs)
        self.add_traits(
            transformer=traitlets.Any(transformer),
            df=traitlets.Any(df)
            )

class IDButton(widgets.Button):
    """ Button that stores model state

    Args:
        model: xplainable model
    """

    def __init__(self, id=None, *args, **kwargs):
        super(IDButton, self).__init__(*args, **kwargs)
        self.add_traits(id=traitlets.Any(id))

class TransformerDropdown(widgets.Dropdown):
    """ Button that stores model state

    Args:
        model: xplainable model
    """

    def __init__(self, transformer=None, *args, **kwargs):
        super(TransformerDropdown, self).__init__(*args, **kwargs)
        self.add_traits(transformer=traitlets.Any(transformer))


class PreprocessorDropdown(widgets.Dropdown):
    """ Dropdown that stores preprocessor state

    Args:
        model: xplainable model
    """

    def __init__(self, preprocessor=None, version=None, metadata={},\
        version_data=None, *args, **kwargs):
        super(PreprocessorDropdown, self).__init__(*args, **kwargs)
        self.add_traits(preprocessor=traitlets.Any(preprocessor))
        self.add_traits(version=traitlets.Any(version))
        self.add_traits(metadata=traitlets.Any(metadata))
        self.add_traits(version_data=traitlets.Any(version_data))


class ModelDropdown(widgets.Dropdown):
    """ Dropdown that stores model state

    Args:
        model: xplainable model
    """

    def __init__(self, model=None, version=None, metadata={}, \
        version_data=None, *args, **kwargs):
        super(ModelDropdown, self).__init__(*args, **kwargs)
        self.add_traits(model=traitlets.Any(model))
        self.add_traits(version=traitlets.Any(version))
        self.add_traits(metadata=traitlets.Any(metadata))
        self.add_traits(version_data=traitlets.Any(version_data))


class ClickResponsiveToggleButtons(widgets.ToggleButtons):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._click_handlers = widgets.CallbackDispatcher()
        self.on_msg(self._handle_button_msg)
        pass

    def on_click(self, callback, remove=False):
        """Register a callback to execute when the button is clicked.

        The callback will be called with one argument, the clicked button
        widget instance.

        Parameters
        ----------
        remove: bool (optional)
            Set to true to remove the callback from the list of callbacks.
        """
        self._click_handlers.register_callback(callback, remove=remove)

    def _handle_button_msg(self, _, content, buffers):
        """Handle a msg from the front-end.

        Parameters
        ----------
        content: dict
            Content of the msg.
        """
        if content.get('event', '') == 'click':
            self._click_handlers(self)

class TextInput:
    
    def __init__(self, label, label_type='h4', label_margin='0 10px 0 0', box_width='200px'):
        self.label = label
        self.label_type = label_type
        self.label_margin = label_margin
        self.box_width = box_width
        
        # Widgets
        self.w_text_input = None
        self.w_label = None
        self.w = widgets.HBox([])
        self.init()

    def init(self):
        self.w_text_input = widgets.Text()        
        self.w_label = widgets.HTML(
            f'<{self.label_type}>{self.label}</{self.label_type}>')
        
        self.w_label.layout = widgets.Layout(margin=self.label_margin)
        self.w_text_input.layout = widgets.Layout(width=self.box_width)
        self.w.children = [self.w_label, self.w_text_input]
        
    def __call__(self, ):
        
        return self.w
    
    @property
    def value(self):
        return self.w_text_input.value
    
    @value.setter
    def value(self, value):
        try:
            self.w_text_input.value = value
        except:
            pass
        
    def hide(self):
        self.w.layout.display = 'none'
    
    def show(self):
        self.w.layout.display = 'flex'

    def disable(self):
        self.w_text_input.disabled = True

    def enable(self):
        self.w_text_input.disabled = False