// Environment variable types for Vite
// This file will be properly resolved after npm install

declare global {
  interface ImportMetaEnv {
    readonly PROD: boolean
    readonly DEV: boolean
    readonly MODE: string
    readonly VITE_API_URL?: string
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv
  }
}

export {}
