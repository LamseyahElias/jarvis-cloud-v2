# CSS Class Reference — Agentic OS Theme

All defined in `static/theme.css`. Use these in `st.markdown(unsafe_allow_html=True)`.

## Layout & Cards
| Class | Purpose |
|-------|---------|
| `.card` | Generic card (bg #141820, border #1e2536, rounded 14px) |
| `.mcard` | Metric card (gradient bg, centered, hover lift) |
| `.mcard-icon` | Large emoji/icon in metric card |
| `.mcard-val` | Big number (JetBrains Mono, 2rem, bold) |
| `.mcard-lbl` | Label below value (uppercase, spaced, muted) |

## Section Headers
| `.sh` | Section header (Space Grotesk, bold, bottom border) |

## Progress Bars
| `.pbar-outer` | Track container (dark bg, 8px height) |
| `.pbar-inner` | Fill bar (use width via inline style) |
| `.pbar-blue/green/purple/amber/pink/cyan` | Fill color variants |

## Badges
| `.bg` | Base badge (inline-block, 6px radius, mono font) |
| `.bg-blue/purple/green/red/amber/pink/cyan` | Color variants |

## Text Colors
| `.c-blue/purple/green/red/amber/pink/cyan/orange` | Accent text |
| `.c-muted` | #6b7280 |
| `.c-dim` | #4b5563 |
| `.c-text` | #d4dae5 |

## Chat
| `.cmsg` | Base chat bubble (14px pad, 14px radius, animated) |
| `.cmsg-user` | User message (blue gradient, right-aligned) |
| `.cmsg-hermes` | Hermes response (dark card bg) |
| `.cmsg-claude` | Claude response (purple-tinted bg) |
| `.cmsg-time` | Timestamp (tiny, dim) |
| `.cmsg-name` | Agent name label (tiny, muted, bold) |

## Goals
| `.gitem` | Goal item (card bg, rounded, hover border) |
| `.gi-pending` | Left border amber |
| `.gi-active` | Left border blue |
| `.gi-done` | Left border green, reduced opacity |

## Identity
| `.icard` | Identity section card |
| `.icard-title` | Title (JetBrains Mono, uppercase, spaced) |

## Knowledge
| `.kb` | Knowledge entry card |

## Upgrade Timeline
| `.uentry` | Timeline entry (left border purple, dot marker) |

## Tools & Skills
| `.tcard` | Tool/skill card (flex, icon left, content right) |
| `.tcard-icon` | Icon container (44px, dark bg, rounded) |

## Animation
| `.anim` | Slide-up fade-in (0.35s) |

## Typography
- Body: `'Space Grotesk', sans-serif`
- Code/values: `'JetBrains Mono', monospace`
- Hero title: `.hero` (gradient text, 2.2rem, 800 weight)
- Hero subtitle: `.hero-sub` (dim, 0.82rem)
