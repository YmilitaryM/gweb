export function useMediaUrl() {
  const config = useRuntimeConfig()
  const base = config.public.mediaBase || config.public.apiBase?.replace(/\/api\/v1$/, '') || ''
  return (id: number | null | undefined): string | null => {
    if (!id) return null
    return `${base}/media/id/${id}`
  }
}
