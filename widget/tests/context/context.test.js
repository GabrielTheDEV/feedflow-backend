// context.test.js
import { describe, it, expect } from 'vitest';
import { getNavigationContext } from '../../src/context.js';

describe('getNavigationContext', () => {
  it('deve retornar url e path atuais', () => {
    const ctx = getNavigationContext();
    expect(typeof ctx.url).toBe('string');
    expect(typeof ctx.path).toBe('string');
    expect(ctx.url).toContain(window.location.href);
    expect(ctx.path).toBe(window.location.pathname);
  });
  it('deve ser seguro mesmo sem window', () => {
    const orig = global.window;
    // @ts-ignore
    delete global.window;
    expect(() => getNavigationContext()).not.toThrow();
    // @ts-ignore
    global.window = orig;
  });
});
