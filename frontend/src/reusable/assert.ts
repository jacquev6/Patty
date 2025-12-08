// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

export default function assert(condition: boolean): asserts condition {
  if (!condition) {
    throw new Error('Assertion failed')
  }
}
