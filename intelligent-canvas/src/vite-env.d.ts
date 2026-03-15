/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_OPENAI_API_KEY: string
  readonly VITE_OPENAI_BASE_URL: string
  readonly VITE_MODEL_NAME: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
