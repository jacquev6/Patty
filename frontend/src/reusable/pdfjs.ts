// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import type PdfjsType from 'pdfjs-dist/types/src/pdf'
// @ts-expect-error: temporary untyped (until next line), and kept private
import * as untypedPdfjs from 'pdfjs-dist/build/pdf'
const pdfjs = untypedPdfjs as typeof PdfjsType

export type PDFDocumentProxy = PdfjsType.PDFDocumentProxy
export type PDFPageProxy = PdfjsType.PDFPageProxy
export type RenderTask = PdfjsType.RenderTask

export default pdfjs
