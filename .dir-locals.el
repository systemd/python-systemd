; Sets emacs variables based on mode.
; A list of (major-mode . ((var1 . value1) (var2 . value2)))
; Mode can be nil, which gives default values.

; NOTE: If you update this file make sure to update .editorconfig too.

((c-mode . ((fill-column . 109)
            (c-basic-offset . 8)
            (eval . (c-set-offset 'substatement-open 0))
            (eval . (c-set-offset 'statement-case-open 0))
            (eval . (c-set-offset 'case-label 0))
            (eval . (c-set-offset 'arglist-intro '++))
            (eval . (c-set-offset 'arglist-close 0))
            (eval . (c-set-offset 'arglist-cont-nonempty '(c-lineup-gcc-asm-reg c-lineup-arglist)))))
 (meson-mode . ((meson-indent-basic . 8)))
 (nil . ((indent-tabs-mode . nil)
         (tab-width . 8)
         (fill-column . 79))) )
