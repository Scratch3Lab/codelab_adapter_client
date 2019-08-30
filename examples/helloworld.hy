(import codelab_adapter_client)
(import time)

(defclass HelloWorldNode [codelab_adapter_client.AdapterNode]
  "LISP hello world node"

  (defn --init-- [self]
    (.--init-- (super))
    (setv self.EXTENSION_ID  "eim"))

  (defn extension-message-handle [self topic payload]
        (print f"the message payload from scratch: {payload}")
        (setv content (list (get payload "content")))
        (.reverse content)  
        (payload.__setitem__ "content" (.join "" content))
        (print payload)
        (self.publish {"payload" payload})
        )

  (defn run [self]
        (while self._running (time.sleep 1)))
)

(setv node (HelloWorldNode))
(.receive-loop-as-thread node)
(.run node)