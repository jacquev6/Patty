<script setup lang="ts">
import { ref, watch } from 'vue'
import jsonStringify from 'json-stringify-pretty-compact'
import { useMagicKeys } from '@vueuse/core'

import type { AdaptedExercise } from '@/apiClient'
import MiniatureScreen from './MiniatureScreen.vue'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'
import FixedColumns from './FixedColumns.vue'

type Example = {
  title: string
  exercise: AdaptedExercise
}

const examples: Example[] = [
  {
    title: 'TransformePhrase',
    exercise: {
      format: 'v1',
      instruction: {
        lines: [
          {
            contents: [
              { kind: 'text', text: 'Transforme' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'chaque' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'couple' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'de' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'phrases' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'pour' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'en' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'faire' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'une' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'seule' },
              { kind: 'text', text: '.' },
            ],
          },
        ],
      },
      example: {
        lines: [
          {
            contents: [
              { kind: 'text', text: 'Léa' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'souffle' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'les' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'bougies' },
              { kind: 'text', text: '.' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'Léo' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'souffle' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'les' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'bougies' },
              { kind: 'text', text: '.' },
            ],
          },
          {
            contents: [
              { kind: 'arrow' },
              { kind: 'text', text: 'Léa' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'et' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'Léo' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'soufflent' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'les' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'bougies' },
              { kind: 'text', text: '.' },
            ],
          },
        ],
      },
      hint: null,
      statement: {
        pages: [
          {
            lines: [
              {
                contents: [
                  { kind: 'text', text: 'a' },
                  { kind: 'text', text: '.' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'Le' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'manchot' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'glisse' },
                  { kind: 'text', text: '.' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'Le' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'pingouin' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'glisse' },
                  { kind: 'text', text: '.' },
                ],
              },
              {
                contents: [{ kind: 'arrow' }, { kind: 'freeTextInput' }],
              },
            ],
          },
          {
            lines: [
              {
                contents: [
                  { kind: 'text', text: 'b' },
                  { kind: 'text', text: '.' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'Kiki' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 's' },
                  { kind: 'text', text: '’' },
                  { kind: 'text', text: 'approche' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'de' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'moi.' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'Loulou' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 's' },
                  { kind: 'text', text: '’' },
                  { kind: 'text', text: 'approche' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'de' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'moi' },
                  { kind: 'text', text: '.' },
                ],
              },
              {
                contents: [{ kind: 'arrow' }, { kind: 'freeTextInput' }],
              },
            ],
          },
        ],
      },
      reference: null,
    },
  },
  {
    title: 'TransformeMot (sur plusieurs pages)',
    exercise: {
      format: 'v1',
      instruction: {
        lines: [
          {
            contents: [
              { kind: 'text', text: 'Écris' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'l' },
              { kind: 'text', text: '’' },
              { kind: 'text', text: 'infinitif' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'des' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'verbes' },
              { kind: 'text', text: '.' },
            ],
          },
        ],
      },
      example: null,
      hint: null,
      statement: {
        pages: [
          {
            lines: [
              {
                contents: [
                  { kind: 'text', text: 'a' },
                  { kind: 'text', text: '.' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'je' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'choisis' },
                  { kind: 'arrow' },
                  { kind: 'freeTextInput' },
                ],
              },
              {
                contents: [
                  { kind: 'text', text: 'il' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'prends' },
                  { kind: 'arrow' },
                  { kind: 'freeTextInput' },
                ],
              },
              {
                contents: [
                  { kind: 'text', text: 'vous' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'salissez' },
                  { kind: 'arrow' },
                  { kind: 'freeTextInput' },
                ],
              },
            ],
          },
          {
            lines: [
              {
                contents: [
                  { kind: 'text', text: 'b' },
                  { kind: 'text', text: '.' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'elle' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'pétille' },
                  { kind: 'arrow' },
                  { kind: 'freeTextInput' },
                ],
              },
              {
                contents: [
                  { kind: 'text', text: 'elle' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'voit' },
                  { kind: 'arrow' },
                  { kind: 'freeTextInput' },
                ],
              },
              {
                contents: [
                  { kind: 'text', text: 'il' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'galope' },
                  { kind: 'arrow' },
                  { kind: 'freeTextInput' },
                ],
              },
              {
                contents: [
                  { kind: 'text', text: 'je' },
                  { kind: 'whitespace' },
                  { kind: 'text', text: 'reçois' },
                  { kind: 'arrow' },
                  { kind: 'freeTextInput' },
                ],
              },
            ],
          },
        ],
      },
      reference: null,
    },
  },
  {
    title: 'CocheMot (et ponctuation)',
    exercise: {
      format: 'v1',
      instruction: {
        lines: [
          {
            contents: [
              { kind: 'text', text: 'Colorie' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'tous' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'les' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'déterminants' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'de' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'ce' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'texte' },
              { kind: 'text', text: '.' },
            ],
          },
        ],
      },
      example: null,
      hint: null,
      statement: {
        pages: [
          {
            lines: [
              {
                contents: [
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'Une' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'éolienne' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'est' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'une' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'centrale' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'électrique' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'comme' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'toutes' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'les' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'autres' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: ':' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'une' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'turbine' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: '(' }],
                  },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'l’' }],
                  },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'hélice' }],
                  },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: ')' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'est' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'mise' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'en' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'rotation' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'par' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'le' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'vent' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: ';' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'elle' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'est' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'couplée' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'à' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'un' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'alternateur' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'qui' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'produit' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'de' }],
                  },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: 'l’électricité' }],
                  },
                  {
                    kind: 'selectableInput',
                    boxed: false,
                    colors: ['#ffff00'],
                    contents: [{ kind: 'text', text: '.' }],
                  },
                ],
              },
            ],
          },
        ],
      },
      reference: null,
    },
  },
  {
    title: 'CochePhrase',
    exercise: {
      format: 'v1',
      instruction: {
        lines: [
          {
            contents: [
              { kind: 'text', text: 'Colorie' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'uniquement' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'les' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'phrases' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'exactes' },
              { kind: 'text', text: '.' },
            ],
          },
        ],
      },
      example: null,
      hint: null,
      statement: {
        pages: [
          {
            lines: [
              {
                contents: [
                  { kind: 'text', text: 'a' },
                  { kind: 'text', text: '.' },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: true,
                    colors: ['#ffff00'],
                    contents: [
                      { kind: 'text', text: 'Une' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'phrase' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'se' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'termine' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'par' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'un' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'point' },
                      { kind: 'text', text: ',' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'un' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'point' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'd' },
                      { kind: 'text', text: '’' },
                      { kind: 'text', text: 'exclamation' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'ou' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'un' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'point' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'd' },
                      { kind: 'text', text: '’' },
                      { kind: 'text', text: 'interrogation' },
                      { kind: 'text', text: '.' },
                    ],
                  },
                ],
              },
              {
                contents: [
                  { kind: 'text', text: 'b' },
                  { kind: 'text', text: '.' },
                  { kind: 'whitespace' },
                  {
                    kind: 'selectableInput',
                    boxed: true,
                    colors: ['#ffff00'],
                    contents: [
                      { kind: 'text', text: 'Si' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'une' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'suite' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'de' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'mots' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'n' },
                      { kind: 'text', text: '’' },
                      { kind: 'text', text: 'a' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'pas' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'de' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'sens,' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'mais' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'qu' },
                      { kind: 'text', text: '’' },
                      { kind: 'text', text: 'elle' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'commence' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'par' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'une' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'majuscule' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'et' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'se' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'termine' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'par' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'un' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'point' },
                      { kind: 'text', text: ',' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'c' },
                      { kind: 'text', text: '’' },
                      { kind: 'text', text: 'est' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'une' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'phrase' },
                      { kind: 'text', text: '.' },
                    ],
                  },
                ],
              },
            ],
          },
        ],
      },
      reference: null,
    },
  },
  {
    title: 'Swappable inputs',
    exercise: {
      format: 'v1',
      instruction: {
        lines: [],
      },
      example: null,
      hint: null,
      statement: {
        pages: [
          {
            lines: [
              {
                contents: [
                  { kind: 'swappableInput', contents: [{ kind: 'text', text: 'A' }] },
                  { kind: 'swappableInput', contents: [{ kind: 'text', text: 'B' }] },
                  { kind: 'swappableInput', contents: [{ kind: 'text', text: 'C' }] },
                ],
              },
            ],
          },
        ],
      },
      reference: null,
    },
  },
  {
    title: 'Edit sentence',
    exercise: {
      format: 'v1',
      instruction: {
        lines: [
          {
            contents: [
              { kind: 'text', text: 'Recopie' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'chaque' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'phrase' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'en' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'rétablissant' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'la' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'ponctuation' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'comme' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'dans' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'l' },
              { kind: 'text', text: "'" },
              { kind: 'text', text: 'exemple' },
              { kind: 'text', text: '.' },
            ],
          },
        ],
      },
      example: {
        lines: [
          {
            contents: [
              { kind: 'text', text: 'la' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'nuit' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'dans' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'le' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'ciel' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'les' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'étoiles' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'brillent' },
            ],
          },
          {
            contents: [
              { kind: 'arrow' },
              { kind: 'text', text: 'La' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'nuit' },
              { kind: 'text', text: ',' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'dans' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'le' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'ciel' },
              { kind: 'text', text: ',' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'les' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'étoiles' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'brillent' },
              { kind: 'text', text: '.' },
            ],
          },
        ],
      },
      hint: null,
      statement: {
        pages: [
          {
            lines: [
              {
                contents: [
                  { kind: 'text', text: 'a' },
                  { kind: 'text', text: '.' },
                  { kind: 'whitespace' },
                  {
                    kind: 'editableTextInput',
                    contents: [
                      { kind: 'text', text: 'souvent' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'dans' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'le' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'noir' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'j' },
                      { kind: 'text', text: "'" },
                      { kind: 'text', text: 'ai' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'peur' },
                    ],
                  },
                ],
              },
            ],
          },
          {
            lines: [
              {
                contents: [
                  { kind: 'text', text: 'b' },
                  { kind: 'text', text: '.' },
                  { kind: 'whitespace' },
                  {
                    kind: 'editableTextInput',
                    contents: [
                      { kind: 'text', text: 'parfois' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'en' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'plein' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'jour' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'j' },
                      { kind: 'text', text: "'" },
                      { kind: 'text', text: 'ai' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'peur' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'aussi' },
                    ],
                  },
                ],
              },
            ],
          },
        ],
      },
      reference: null,
    },
  },
]

const fullScreenIndex = ref<number | null>(null)
const { Escape } = useMagicKeys()

watch(Escape, () => {
  fullScreenIndex.value = null
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <template v-for="(example, exampleIndex) in examples" :key="example.title">
      <h1>{{ example.title }}</h1>
      <FixedColumns :columns="[1, 1]">
        <template #col-1>
          <pre>{{ jsonStringify(example.exercise) }}</pre>
        </template>
        <template #col-2>
          <MiniatureScreen :fullScreen="fullScreenIndex === exampleIndex">
            <AdaptedExerciseRenderer
              :navigateUsingArrowKeys="fullScreenIndex === exampleIndex"
              :adaptedExercise="example.exercise"
            />
            <button v-if="fullScreenIndex === exampleIndex" class="exitFullScreen" @click="fullScreenIndex = null">
              Exit full screen (Esc)
            </button>
          </MiniatureScreen>
          <button @click="fullScreenIndex = exampleIndex">Full screen</button>
        </template>
      </FixedColumns>
    </template>
  </div>
</template>

<style scoped>
button.exitFullScreen {
  position: absolute;
  left: 50%;
  transform: translate(-50%, 0);
  bottom: 2rem;
}
</style>
