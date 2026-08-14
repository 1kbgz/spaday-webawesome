# Why WebAwesome is a peer package

Spaday core defines a serializable component model and browser runtime. WebAwesome defines an
independent design system with its own release cadence, catalog, CSS, and runtime. Keeping those layers
in separate packages lets each evolve without making one component library a core default.

Installation and activation are intentionally separate. Installing `spaday-webawesome` makes typed
Python classes and a component-package entry point available. Passing `packages=["webawesome"]` opts a
page into its CSS and registration bundle. Applications that use another catalog do not download or
execute WebAwesome assets.

The generated Python module is committed because static type checkers need concrete class signatures.
The source Custom Elements Manifest is committed beside it, and a drift test regenerates the module to
keep both representations aligned.

Forms and `Tabs` live here for the same ownership reason: their structure is specifically composed from
`wa-*` elements. Core shell components stay catalog-neutral, while this package maps WebAwesome theme
tokens onto core shell variables so both layers still look coherent when combined.
