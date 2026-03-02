// consoleBuffer.test.js
import { instrumentConsole, getConsoleBuffer, resetConsoleBuffer } from '../../src/consoleBuffer.js';

describe('consoleBuffer', () => {

  beforeEach(() => { resetConsoleBuffer(); });

  it('bufferiza logs e mantém FIFO', () => {
    instrumentConsole();
    for (let i = 0; i < 55; i++) console.log('log', i);
    const buf = getConsoleBuffer();
    expect(buf.length).toBe(50);
    expect(buf[0].message).toContain('log 5');
    expect(buf[49].message).toContain('log 54');
  });

  it('não quebra comportamento original', () => {
    instrumentConsole();
    expect(() => console.info('info')).not.toThrow();
    expect(() => console.warn('warn')).not.toThrow();
    expect(() => console.error('error')).not.toThrow();
  });

  it('trunca mensagens longas', () => {
    instrumentConsole();
    const msg = 'a'.repeat(2000);
    console.log(msg);
    const buf = getConsoleBuffer();
    expect(buf[buf.length-1].message.length).toBeLessThanOrEqual(1000);
  });

  it('é idempotente', () => {
    instrumentConsole();
    instrumentConsole();
    console.log('idempotente');
    const buf = getConsoleBuffer();
    expect(buf[buf.length-1].message).toContain('idempotente');
  });
  
});
