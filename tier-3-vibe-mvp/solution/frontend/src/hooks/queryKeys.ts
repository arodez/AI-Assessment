export const eventKeys = {
  all: ['events'] as const,
  list: () => [...eventKeys.all, 'list'] as const,
  detail: (id: number) => [...eventKeys.all, 'detail', id] as const,
  attendance: (id: number) => [...eventKeys.all, 'detail', id, 'attendance'] as const,
};
