import logging

from typing import Any, Dict, List, Type


class Registry:
    """
    A factory register pattern
    
    How to Use this Pattern
    =======================

    1. Define an abstract class to register the concrete implementations

    class Model(metaclass=ABCMeta):              # It must be an Abstract class
        '''Image classification architecture.'''  # It must have a docstring

        @abstractmethod
        def __call__(self, *args: Any, **kwds: Any) -> Any:
            '''A method'''

    2. Create the component registry.

    ModelRegistry = Registry(Model)

    3. Register concrete components

    @ModelRegistry.register
    class ResNet50(Model):
        '''A model with support for a single head'''

        def __init__(self, num_classes: int) -> None:
            super().__init__()
            self.num_classes = num_classes

        def __call__(self, *args: Any, **kwds: Any) -> Any:
            # concrete implementation

    4. Build from registry

    resnet = ModelRegistry.build('ResNet50', build_arguments={'num_classes': 1})
    """

    def __init__(self, class_type: Type) -> None:
        self.class_type = class_type
        self.name = class_type.__name__
        self._help = class_type.__doc__
        self._factories: Dict[str, class_type] = {}

    def register(self, class_type: Type) -> Type:
        if not issubclass(class_type, self.class_type):
            logging.error(f'{class_type.__name__} is not a subclass of {self.class_type}.')
            raise ValueError(f'{class_type.__name__} is not a valid subclass.')
        if class_type.__name__ in self._factories:
            logging.error(f'{class_type.__name__} already on registry.')
            raise ValueError(f'{class_type.__name__} already registered.')
        logging.debug(f'Add {class_type.__name__} to {self.name} registry.')
        self._factories[class_type.__name__] = class_type
        return class_type

    def build(self, name: str, build_arguments: Dict[str, Any] = {}) -> Any:
        if name not in self._factories:
            raise ValueError('`name` not in registry', name)
        logging.debug(f'Building {name}. Build Arguments: {build_arguments}')
        instance = self._factories[name](**build_arguments)
        return instance

    def list_availables(self) -> List[str]:
        """List available factories.

        Returns:
            List[str]: List of available factories
        """
        return list(self._factories.keys())

    def __str__(self) -> str:
        """Build a string representation with the available factories."""
        header = f'{self.name} Registry\n\n'
        header += f'Class Type: {self.class_type.__name__}\n\n'
        header += f'Class Description: {self._help}\n\n'
        table = 'Registered Factories:\n\n'
        table += '{:<30}{}\n'.format('Name', 'Description')
        table += '{:<30}{}\n'.format('----', '-----------')
        for name, class_type in self._factories.items():
            doc = class_type.__doc__ if class_type.__doc__ else ''
            table += '{:<30}{}\n'.format(name, doc)
        return header + table
