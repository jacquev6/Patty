// MALIN Platform https://malin.cahiersfantastiques.fr/
// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

import { makePagesGroups, mergePagesGroups } from './PdfRangesFormInputs.vue'

describe('PdfRangeFormInputs', () => {
  it('makes pages groups', () => {
    expect(makePagesGroups(1, 1, [], 5)).to.deep.eq([{ first: 1, last: 1, excluded: [] }])
    expect(makePagesGroups(1, 5, [], 5)).to.deep.eq([{ first: 1, last: 5, excluded: [] }])
    expect(makePagesGroups(1, 6, [], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [] },
      { first: 6, last: 6, excluded: [] },
    ])
    expect(makePagesGroups(1, 9, [], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [] },
      { first: 6, last: 9, excluded: [] },
    ])
    expect(makePagesGroups(1, 10, [], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [] },
      { first: 6, last: 10, excluded: [] },
    ])
    expect(makePagesGroups(1, 11, [], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [] },
      { first: 6, last: 10, excluded: [] },
      { first: 11, last: 11, excluded: [] },
    ])
    expect(makePagesGroups(1, 15, [], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [] },
      { first: 6, last: 10, excluded: [] },
      { first: 11, last: 15, excluded: [] },
    ])

    expect(makePagesGroups(1, 13, [], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [] },
      { first: 6, last: 10, excluded: [] },
      { first: 11, last: 13, excluded: [] },
    ])
    expect(makePagesGroups(1, 13, [1], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [1] },
      { first: 6, last: 10, excluded: [] },
      { first: 11, last: 13, excluded: [] },
    ])
    expect(makePagesGroups(1, 13, [5], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [5] },
      { first: 6, last: 10, excluded: [] },
      { first: 11, last: 13, excluded: [] },
    ])
    expect(makePagesGroups(1, 13, [6], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [] },
      { first: 6, last: 10, excluded: [6] },
      { first: 11, last: 13, excluded: [] },
    ])
    expect(makePagesGroups(1, 13, [10], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [] },
      { first: 6, last: 10, excluded: [10] },
      { first: 11, last: 13, excluded: [] },
    ])
    expect(makePagesGroups(1, 13, [11], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [] },
      { first: 6, last: 10, excluded: [] },
      { first: 11, last: 13, excluded: [11] },
    ])
    expect(makePagesGroups(1, 13, [13], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [] },
      { first: 6, last: 10, excluded: [] },
      { first: 11, last: 13, excluded: [13] },
    ])

    expect(makePagesGroups(1, 13, [1, 6, 11], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [1] },
      { first: 6, last: 10, excluded: [6] },
      { first: 11, last: 13, excluded: [11] },
    ])

    expect(makePagesGroups(1, 13, [6, 7, 8, 9, 10], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [] },
      { first: 11, last: 13, excluded: [] },
    ])

    expect(makePagesGroups(1, 13, [11, 12, 13], 5)).to.deep.eq([
      { first: 1, last: 5, excluded: [] },
      { first: 6, last: 10, excluded: [] },
    ])

    expect(makePagesGroups(4, 13, [], 5)).to.deep.eq([
      { first: 4, last: 5, excluded: [] },
      { first: 6, last: 10, excluded: [] },
      { first: 11, last: 13, excluded: [] },
    ])

    expect(makePagesGroups(5, 13, [], 5)).to.deep.eq([
      { first: 5, last: 5, excluded: [] },
      { first: 6, last: 10, excluded: [] },
      { first: 11, last: 13, excluded: [] },
    ])

    expect(makePagesGroups(7, 9, [], 5)).to.deep.eq([{ first: 7, last: 9, excluded: [] }])
    expect(makePagesGroups(17, 19, [18], 5)).to.deep.eq([{ first: 17, last: 19, excluded: [18] }])
    expect(makePagesGroups(12, 19, [18], 5)).to.deep.eq([
      { first: 12, last: 15, excluded: [] },
      { first: 16, last: 19, excluded: [18] },
    ])
    expect(makePagesGroups(2, 4, [2, 3, 4], 5)).to.deep.eq([])
    expect(makePagesGroups(7, 9, [7, 8, 9], 5)).to.deep.eq([])
  })

  it('merges pages groups', () => {
    expect(mergePagesGroups([{ first: 1, last: 5, excluded: [] }])).to.deep.eq([[1, 5]])
    expect(mergePagesGroups([{ first: 1, last: 5, excluded: [3] }])).to.deep.eq([
      [1, 2],
      [4, 5],
    ])
    expect(
      mergePagesGroups([
        { first: 1, last: 5, excluded: [] },
        { first: 6, last: 10, excluded: [] },
      ]),
    ).to.deep.eq([[1, 10]])
    expect(
      mergePagesGroups([
        { first: 1, last: 5, excluded: [] },
        { first: 6, last: 10, excluded: [10] },
      ]),
    ).to.deep.eq([[1, 9]])
    expect(
      mergePagesGroups([
        { first: 1, last: 5, excluded: [1] },
        { first: 6, last: 10, excluded: [10] },
      ]),
    ).to.deep.eq([[2, 9]])
    expect(
      mergePagesGroups([
        { first: 1, last: 5, excluded: [5] },
        { first: 6, last: 10, excluded: [6] },
      ]),
    ).to.deep.eq([
      [1, 4],
      [7, 10],
    ])
    expect(
      mergePagesGroups([
        { first: 1, last: 5, excluded: [] },
        { first: 6, last: 10, excluded: [8] },
      ]),
    ).to.deep.eq([
      [1, 7],
      [9, 10],
    ])
  })
})
